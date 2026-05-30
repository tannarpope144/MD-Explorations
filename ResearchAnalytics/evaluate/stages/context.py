from collections.abc import Callable
from ..config import ModelClass
from ..search.base import SearchClient, SearchResult


class SearchBudgetExceeded(RuntimeError):
    pass


class ResearchContext:
    """Shared dependency passed to every stage: budgeted search + class-routed LLM."""
    def __init__(self, search: SearchClient,
                 llm_for: Callable[[ModelClass], tuple],
                 max_searches: int):
        self._search = search
        self._llm_for = llm_for
        self.max_searches = max_searches
        self.searches_used = 0

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if self.searches_used >= self.max_searches:
            raise SearchBudgetExceeded(f"budget {self.max_searches} reached")
        self.searches_used += 1
        try:
            return self._search.search(query, limit)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[evaluate] search failed ({type(e).__name__}): {e}", flush=True)
            raise SearchBudgetExceeded("search provider error") from e

    def scrape(self, url: str) -> str:
        try:
            return self._search.scrape(url)
        except Exception as e:
            print(f"[evaluate] scrape failed for {url}: {e}", flush=True)
            return ""

    def llm(self, cls: ModelClass):
        """Returns (client, model) for the requested class."""
        return self._llm_for(cls)
