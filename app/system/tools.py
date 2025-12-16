"""module to implement tools to be used"""
import os
from llama_index.core.workflow import Context
from tavily import AsyncTavilyClient

# Prefer conventional uppercase env var names
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
if not TAVILY_API_KEY:
    raise RuntimeError("Missing required environment variable 'TAVILY_API_KEY'. Set it to your Tavily API key.")

tavily_api_key = TAVILY_API_KEY

# tools to be distributed amongst the agents


async def search_web(query: str) -> str:

    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key=tavily_api_key)
    result = await client.search(query, max_results=1)
    if result.get("answer"):
        return result["answer"]
    return 'could not get answers'


async def record_notes(ctx: Context, notes: str,
                       notes_title: str = "Untitled Notes") -> str:
    """Useful for recording notes on a given topic."""
    current_state = await ctx.get("state")
    if "research_notes" not in current_state:
        current_state["research_notes"] = {}
    current_state["research_notes"][notes_title] = notes
    await ctx.set("state", current_state)
    return "Notes recorded."


async def write_report(ctx: Context, report_content: str) -> str:
    """Useful for writing a report on a given topic."""
    current_state = await ctx.get("state")
    current_state["report_content"] = report_content
    await ctx.set("state", current_state)
    return "Report written."


async def review_report(ctx: Context, review: str) -> str:
    """Useful for reviewing a report and providing feedback."""
    current_state = await ctx.get("state")
    current_state["review"] = review
    await ctx.set("state", current_state)
    return "Report reviewed."