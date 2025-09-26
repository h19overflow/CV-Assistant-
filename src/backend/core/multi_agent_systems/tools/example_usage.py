"""
Example usage of the Perplexity search tool with pydantic_ai agents
"""

import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel

from .perplexity_search_tool import perplexity_search_tool

class SearchDeps(BaseModel):
    """Dependencies for search agent."""
    pass

# Create an agent with the Perplexity search tool
search_agent = Agent(
    'gemini-2.5-flash-lite',
    deps_type=SearchDeps,
    tools=[perplexity_search_tool]
)

async def example_usage():
    """Example of using the Perplexity search tool with an agent."""

    # Single query example
    result = await search_agent.run(
        "Search for information about 'Claude AI' and summarize the results",
        deps=SearchDeps()
    )
    print("Single query result:", result.output)

    # Multiple queries example
    result = await search_agent.run(
        "Search for 'Python async programming' and 'FastAPI best practices' and compare them",
        deps=SearchDeps()
    )
    print("Multiple query result:", result.output)

if __name__ == "__main__":
    asyncio.run(example_usage())