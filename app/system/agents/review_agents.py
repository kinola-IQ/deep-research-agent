from llama_index.core.agent.workflow import FunctionAgent
from ..tools import review_report
from ..model.model_loader import get_model


def get_review_agent():
    """Create and return the review agent using the current model."""
    llm = get_model()
    if llm is None:
        raise RuntimeError("Model not loaded yet")

    return FunctionAgent(
        tools=[review_report],
        llm=llm,
        verbose=False,
        system_prompt="""You are part of a deep research system.
      Your job is to review a report that's been written and suggest
      questions that could have been asked to produce a more comprehensive
      report than the current version, or to decide that the current
      report is comprehensive enough."""
    )
