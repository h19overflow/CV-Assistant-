"""
Perplexity search tool for pydantic_ai agents
"""

import os
import logging
from typing import List, Union, Optional
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

try:
    from perplexity import Perplexity
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

class SearchResult(BaseModel):
    """Individual search result from Perplexity."""
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    snippet: Optional[str] = Field(default=None, description="Text snippet from the result")

class PerplexitySearchResponse(BaseModel):
    """Complete response from Perplexity search."""
    results: List[SearchResult] = Field(description="List of search results")
    query_used: str = Field(description="The query that was executed")
    total_results: int = Field(description="Total number of results returned")

class PerplexitySearchTool:
    """Perplexity search tool for pydantic_ai agents."""

    def __init__(self):
        """Initialize the Perplexity search tool."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self._client = None
        if PERPLEXITY_AVAILABLE:
            try:
                self._client = Perplexity()
                self.logger.info("Perplexity client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Perplexity client: {e}")
        else:
            self.logger.error("Perplexity library not available")

    def search(self, query: Union[str, List[str]]) -> PerplexitySearchResponse:
        """
        Search using Perplexity API.

        Args:
            query: Single query string or list of query strings

        Returns:
            PerplexitySearchResponse: Search results with metadata

        Raises:
            RuntimeError: If Perplexity is not available or search fails
        """
        if not PERPLEXITY_AVAILABLE:
            raise RuntimeError("Perplexity library not available. Install with: pip install perplexity-ai")

        if not self._client:
            raise RuntimeError("Perplexity client not initialized")

        try:
            # Ensure query is a list
            query_list = [query] if isinstance(query, str) else query
            query_str = query_list[0] if len(query_list) == 1 else ", ".join(query_list)

            # Perform search
            search_response = self._client.search.create(query=query_list)

            # Convert results to our schema
            results = []
            for result in search_response.results:
                search_result = SearchResult(
                    title=result.title,
                    url=result.url,
                    snippet=getattr(result, 'snippet', None)
                )
                results.append(search_result)

            response = PerplexitySearchResponse(
                results=results,
                query_used=query_str,
                total_results=len(results)
            )

            self.logger.info(f"Search completed: {len(results)} results for query '{query_str}'")
            return response

        except Exception as e:
            self.logger.error(f"Perplexity search failed: {e}")
            raise RuntimeError(f"Search failed: {e}")

# Global instance for tool registration
_perplexity_tool = PerplexitySearchTool()

def create_perplexity_search_tool() -> Tool:
    """
    Create a pydantic_ai Tool for Perplexity search.

    Returns:
        Tool: Configured pydantic_ai tool for Perplexity search
    """
    def perplexity_search(query: Union[str, List[str]]) -> PerplexitySearchResponse:
        """
        Search the web using Perplexity AI.

        Args:
            query: Search query (string) or multiple queries (list of strings)

        Returns:
            PerplexitySearchResponse: Search results with titles, URLs, and snippets
        """
        return _perplexity_tool.search(query)

    return Tool(perplexity_search, description="Search the web using Perplexity AI for current information")

# Export the tool function directly for convenience
perplexity_search_tool = create_perplexity_search_tool()