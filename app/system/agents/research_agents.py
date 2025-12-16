"""Module for research agents.

This module exposes factory functions that create agents at runtime using
the currently loaded model. Creating agents lazily avoids binding a
stale `None` model at import time and avoids blocking imports.
"""

from llama_index.core.agent.workflow import FunctionAgent
from ..tools import search_web, record_notes
from ..model.model_loader import get_model


def get_question_agent():
    """Return a question-generation agent initialized with the current model.

    Raises RuntimeError if the model is not yet loaded.
    """
    llm = get_model()
    if llm is None:
        raise RuntimeError("Model not loaded yet")

    return FunctionAgent(
        tools=[],
        llm=llm,
        verbose=False,
        system_prompt="""You are part of a deep research system.
      Given a research topic, you should come up with a bunch of questions
      that a separate agent will answer in order to write a comprehensive
      report on that topic. To make it easy to answer the questions separately,
      you should provide the questions one per line. Don't include markdown
      or any preamble in your response, just a list of questions."""
    )


def get_research_agent():
    """Return the research agent which can search the web and record notes."""
    llm = get_model()
    if llm is None:
        raise RuntimeError("Model not loaded yet")

    return FunctionAgent(
        system_prompt=(
            "You are the ResearchAgent that can search the web for\
            information on a given topic and record notes on the topic. "
            "Once notes are recorded, you should hand off \
            control to a seperate Agent to write a report on the topic."
            "if search results turn up empty, signify without fail."
        ),
        llm=llm,
        tools=[search_web, record_notes],
        verbose=False,
    )
