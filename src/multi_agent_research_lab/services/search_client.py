"""Search client abstraction for ResearcherAgent."""

from ddgs import DDGS
from multi_agent_research_lab.core.schemas import SourceDocument

class SearchClient:
    """Provider-agnostic search client using DuckDuckGo."""
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        results = []
        try:
            ddg_results = self.ddgs.text(query, max_results=max_results)
            for r in ddg_results:
                results.append(SourceDocument(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")
                ))
        except Exception as e:
            # Silently fallback or log
            print(f"Search failed: {e}")
        return results
