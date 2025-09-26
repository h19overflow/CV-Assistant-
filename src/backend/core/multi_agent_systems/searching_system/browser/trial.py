import requests
import json


class SearXNGClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def search(self, query, engines=None, categories=None, format="json"):
        """
        Search using SearXNG API

        Args:
            query: Search query string
            engines: List of engines ['google', 'bing', 'duckduckgo']
            categories: List of categories ['general', 'it', 'science']
            format: Response format ('json' or 'html')
        """
        params = {
            "q": query,
            "format": format
        }

        if engines:
            params["engines"] = ",".join(engines)
        if categories:
            params["categories"] = ",".join(categories)

        try:
            response = requests.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()

            if format == "json":
                return response.json()
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            return None


# Usage example
searx = SearXNGClient()

# Basic search
results = searx.search("machine learning frameworks 2025")

# Domain-specific search
ai_results = searx.search(
    "transformer architecture",
    engines=["google"],
    categories=["science", "it"]
)

# Process results
if results and 'results' in results:
    for result in results['results'][:5]:  # Top 5 results
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Content: {result['content'][:200]}...")
        print("-" * 50)
