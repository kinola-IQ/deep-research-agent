import pytest

from app.system.model import model_loader
from app.system.agents import research_agents, write_agents, review_agents
from llama_index.core.agent.workflow import FunctionAgent


def test_get_model_initially_none():
    # Unless load_model has been called, the model should be None
    assert model_loader.get_model() is None


def test_get_question_agent_raises_when_model_missing(monkeypatch):
    monkeypatch.setattr(model_loader, "get_model", lambda: None)
    with pytest.raises(RuntimeError):
        research_agents.get_question_agent()


def test_get_question_agent_returns_agent(monkeypatch):
    # Provide a fake LLM object
    fake_llm = object()
    monkeypatch.setattr(model_loader, "get_model", lambda: fake_llm)
    agent = research_agents.get_question_agent()
    assert isinstance(agent, FunctionAgent)


def test_get_report_and_review_agents_return_agent(monkeypatch):
    fake_llm = object()
    monkeypatch.setattr(model_loader, "get_model", lambda: fake_llm)
    report_agent = write_agents.get_report_agent()
    review_agent = review_agents.get_review_agent()
    assert isinstance(report_agent, FunctionAgent)
    assert isinstance(review_agent, FunctionAgent)
