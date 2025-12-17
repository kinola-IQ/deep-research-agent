"""module to hgandle workflow orchestration"""
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step
)

# third pary modules
from ..utils.events import (
    GenerateEvent,
    QuestionEvent,
    AnswerEvent,
    ProgressEvent,
    FeedbackEvent,
    ReviewEvent,
)


# planner agent
class WorkflowClass(Workflow):
    """
    This is central hub that controls how the agents interacts
    to answer questions
    """
    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> GenerateEvent:
        self.question_agent = ev.question_agent
        self.answer_agent = ev.answer_agent
        self.report_agent = ev.report_agent
        self.review_agent = ev.review_agent
        self.review_cycles = 0

        ctx.write_event_to_stream(ProgressEvent(msg="Starting research"))

        return GenerateEvent(research_topic=ev.research_topic)

    @step
    async def generate_questions(self, ctx: Context, ev: GenerateEvent | FeedbackEvent) -> QuestionEvent:

        await ctx.store.set("research_topic", ev.research_topic)
        ctx.write_event_to_stream(ProgressEvent(msg=f"Research topic is {ev.research_topic}"))

        prompt = f"""Generate some questions on the topic <topic>{ev.research_topic}</topic>."""

        if isinstance(ev, FeedbackEvent):
            ctx.write_event_to_stream(ProgressEvent(msg=f"Got feedback: {ev.feedback}"))
            prompt += f"""You have previously researched this topic and
                got the following feedback, consisting of additional questions
                you might want to ask: <feedback>{ev.feedback}</feedback>.
                Keep this in mind when formulating your questions."""

        result = await self.question_agent.run(user_msg=prompt)

        # Some basic string manipulation to get separate questions
        lines = str(result).split("\n")
        questions = [line.strip() for line in lines if line.strip() != ""]

        # Record how many answers we're going to need to wait for
        await ctx.store.set("total_questions", len(questions))

        # Fire off multiple Answer Agents
        for question in questions:
            ctx.send_event(QuestionEvent(question=question))

    @step
    async def answer_question(self, ctx: Context, ev: QuestionEvent) -> AnswerEvent:

        result = await self.answer_agent.run(user_msg=f"""Research the answer to this
          question: <question>{ev.question}</question>. You can use web
          search to help you find information on the topic, as many times
          as you need. Return just the answer without preamble or markdown.""")

        ctx.write_event_to_stream(ProgressEvent(msg=f"""Received question {ev.question}
            Came up with answer: {str(result)}"""))

        return AnswerEvent(question=ev.question,answer=str(result))

    @step
    async def write_report(self, ctx: Context, ev: AnswerEvent) -> ReviewEvent:

        # CODE: store the answers in a variable
        research = ctx.collect_events(ev, [AnswerEvent] * await ctx.get("total_questions"))
        # If we haven't received all the answers yet, this will be None
        if research is None:
            ctx.write_event_to_stream(ProgressEvent(msg="Collecting answers..."))
            return None

        ctx.write_event_to_stream(ProgressEvent(msg="Generating report..."))

        # Aggregate the questions and answers
        all_answers = ""
        for q_and_a in research:
            all_answers += f"Question: {q_and_a.question}\nAnswer: {q_and_a.answer}\n\n"

        # Prompt the report
        result = await self.report_agent.run(user_msg=f"""You are part of a deep research system.
          You have been given a complex topic on which to write a report:
          <topic>{await ctx.get("research_topic")}.

          Other agents have already come up with a list of questions about the
          topic and answers to those questions. Your job is to write a clear,
          thorough report that combines all the information from those answers.

          Here are the questions and answers:
          <questions_and_answers>{all_answers}</questions_and_answers>""")

        return ReviewEvent(report=str(result))

    @step
    async def review(self, ctx: Context, ev: ReviewEvent) -> StopEvent | FeedbackEvent:

        # CODE: call the review agent at this step
        result = await self.review_agent.run(user_msg=f"""You are part of a deep research system.
          You have just written a report about the topic {await ctx.get("research_topic")}.
          Here is the report: <report>{ev.report}</report>
          Decide whether this report is sufficiently comprehensive.
          If it is, respond with just the string "ACCEPTABLE" and nothing else.
          If it needs more research, suggest some additional questions that could
          have been asked.""")

        self.review_cycles += 1

        # Either it's okay or we've already gone through 3 cycles
        if str(result) == "ACCEPTABLE" or self.review_cycles >= 3:
            return StopEvent(result=ev.report)
        else:
            ctx.write_event_to_stream(ProgressEvent(msg="Sending feedback"))
            return FeedbackEvent(
                research_topic=await ctx.get("research_topic"),
                feedback=str(result)
            )