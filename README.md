Deep Research Agent
===================

A FastAPI service that orchestrates a multi-agent research workflow. It asks clarifying questions, performs web research, drafts a markdown report, and reviews the output with iterative feedback. Responses can be streamed via Server-Sent Events (SSE) for real-time progress updates.

Features
--------
- Workflow-driven orchestration (llama_index workflow) coordinating question, research, report-writing, and review agents.
- Web research via Tavily, with captured notes persisted in workflow state.
- Report drafting and automatic review cycles (up to three passes) for completeness.
- SSE streaming endpoint to monitor progress events and receive the final report.
- Model loader with retry/backoff and provider switching (Ollama) for robustness.
- Request/response logging middleware for latency visibility.

Architecture
------------
- `app/main.py` boots FastAPI, registers logging middleware, and mounts routes under `/v1`.
- `app/interface/routes.py` exposes synchronous and streaming endpoints, instantiates the workflow, and wires the agents.
- `app/system/agents/` defines the individual agents (question, research, report, review) powered by the shared LLM.
- `app/system/agents/workflow.py` coordinates the multi-step process, fans out question answering, aggregates results, drafts, and reviews.
- `app/system/tools.py` supplies tool functions used by agents (web search, note taking, report write/review state storage).
- `app/system/model/` loads the LLM via `LLMSwitcher`, currently targeting local Ollama models.
- `app/system/utils/` holds events, schemas, and logging utilities.

Prerequisites
-------------
- Python 3.11 recommended.
- Ollama installed and running locally with access to the models in `OllamaClass.model_list` (default: `qwen3:4b`, `gemma3:4b`).
- Tavily API key available as environment variable `TAVILY_API_KEY`.
- (Optional) `uvicorn` for local serving during development.

Installation
------------
1) Clone the repository and enter the project directory.  
2) Create a virtual environment and activate it.  
3) Install dependencies (adjust versions as needed):
```
pip install -r requirements.txt
```
4) Export required environment variables:
```
set TAVILY_API_KEY=YOUR_KEY_HERE        # Windows cmd
# or: $env:TAVILY_API_KEY="YOUR_KEY_HERE"  # PowerShell
```

Running the API
---------------
Start the FastAPI app with uvicorn:
```
uvicorn app.main:app --host 127.0.0.1 --port 8501
```
The lifespan handler loads the LLM at startup with retries.

API Usage
---------
- Base path: `/v1`

1) Synchronous research  
`POST /v1/agent`  
Body:
```
{
  "text": "How will low-earth orbit satellite demand evolve by 2030?"
}
```
Response:
```
{
  "response": "<final markdown report>"
}
```

2) Streaming research (SSE)  
`POST /v1/agent/stream`  
The endpoint streams `progress` events followed by a final `response` event. Example curl:
```
curl -N -H "Content-Type: application/json" \
  -X POST http://127.0.0.1:8501/v1/agent/stream \
  -d '{"text": "State of quantum error correction"}'
```
You will receive lines like:
```
data: {"type": "progress", "message": "Starting research"}
...
data: {"type": "final", "response": "<final markdown report>"}
```

Configuration Notes
-------------------
- Model selection: edit `app/system/model/llms.py` (`OllamaClass.model_list`) to reorder or replace model candidates. The first model loading in <=5s is used.
- Workflow timeout: instantiated in `WorkflowClass` via `WorkflowClass(timeout=300)` in `routes.py`.
- Tooling: `search_web` uses Tavily; ensure the API key is set. `record_notes`, `write_report`, and `review_report` persist data in the workflow context.
- Logging: HTTP request timing is logged through `register_http_logging` in `app/system/utils/logger.py`.

Project Layout
--------------
```
app/
  main.py                 # FastAPI entrypoint
  interface/routes.py     # HTTP endpoints and SSE streaming
  system/
    agents/               # Agent definitions and workflow orchestration
    model/                # LLM loader/switcher (Ollama)
    tools.py              # Agent tools (search, notes, report helpers)
    utils/                # Events, schemas, logging utilities
```

Development Tips
----------------
- When adjusting prompts or agent behavior, update the corresponding agent in `app/system/agents/`.
- To change retry/backoff behavior for model loading, edit `load_model` in `app/system/model/model_loader.py`.
- Tests are currently not provided; consider adding integration tests that exercise `/v1/agent` and `/v1/agent/stream`.

Troubleshooting
---------------
- Model fails to load: verify Ollama is running and models are pulled (`ollama pull qwen3:4b`, etc.). The loader retries with exponential backoff.
- Empty search results: Tavily API key missing or quota issues; check `tavily_api_key` env variable.
- Streaming client issues: ensure the client supports SSE and does not buffer the connection.

incoming updates
----------------
- Modification of the llm_switcher module to make it more robustness
- Addition of custom exceptions for implementing easy to understand error exceptions
- addition of test modules to validate application function
- implemention of a user interface
- implementation of an evaluation module
- persistence of logs to memory
