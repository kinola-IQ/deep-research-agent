import json
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.system import model_loader
from app.system.agents import research_agents, write_agents, review_agents


class MockAgent:
    def __init__(self, result):
        self._result = result

    async def run(self, *args, **kwargs):
        return self._result


client = TestClient(app)


def setup_fake_environment(monkeypatch, report="FINAL REPORT", review_response="ACCEPTABLE"):
    # Prevent the real load_model from running during startup
    monkeypatch.setattr(main_module, "load_model", lambda: None)
    # Set a fake model value
    monkeypatch.setattr(model_loader, "get_model", lambda: object())
    # Monkeypatch agents to simple mocks
    monkeypatch.setattr(research_agents, "get_question_agent", lambda: MockAgent("Q1\nQ2"))
    monkeypatch.setattr(research_agents, "get_research_agent", lambda: MockAgent("Answer"))
    monkeypatch.setattr(write_agents, "get_report_agent", lambda: MockAgent(report))
    monkeypatch.setattr(review_agents, "get_review_agent", lambda: MockAgent(review_response))


def test_agent_endpoint_returns_report(monkeypatch):
    setup_fake_environment(monkeypatch)

    resp = client.post("/v1/agent", json={"text": "test topic"})
    assert resp.status_code == 200
    body = resp.json()
    assert "response" in body
    assert body["response"] == "FINAL REPORT"


def test_agent_returns_503_when_model_missing(monkeypatch):
    # Simulate model missing
    monkeypatch.setattr(model_loader, "get_model", lambda: None)
    resp = client.post("/v1/agent", json={"text": "test topic"})
    assert resp.status_code == 503


def test_health_endpoint_reports_model_status(monkeypatch):
    # Model not loaded
    monkeypatch.setattr(model_loader, "get_model", lambda: None)
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json().get("model_loaded") is False

    # Model loaded
    monkeypatch.setattr(model_loader, "get_model", lambda: object())
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json().get("model_loaded") is True


def test_agent_stream_endpoint_sends_progress_and_final(monkeypatch):
    setup_fake_environment(monkeypatch)

    with client.stream("POST", "/v1/agent/stream", json={"text": "test topic"}) as resp:
        assert resp.status_code == 200
        lines = []
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                payload = json.loads(line[len("data: "):])
                lines.append(payload)

        # Ensure we saw at least one progress event and one final event
        types = [p.get("type") for p in lines]
        assert "progress" in types
        assert "final" in types
        final_payloads = [p for p in lines if p.get("type") == "final"]
        assert final_payloads
        assert final_payloads[-1]["response"] == "FINAL REPORT"
