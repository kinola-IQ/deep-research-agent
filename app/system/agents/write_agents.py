from llama_index.core.agent.workflow import FunctionAgent
from ..model.model_loader import get_model
from ..tools import write_report


def get_report_agent():
    """Create a report-writing agent using the current model."""
    llm = get_model()
    if llm is None:
        raise RuntimeError("Model not loaded yet")

    return FunctionAgent(
        tools=[write_report],
        llm=llm,
        verbose=False,
        system_prompt="""You are part of a deep research system.
      Given a set of answers to a set of questions, your job is to combine
      them all into a comprehensive report on the topic.
      Your report should be in a markdown format. \
      The content should be grounded in the research notes. 
      Once the report is written,\
      you should get feedback from a seperate agent.
    """
    )
