import httpx
from .base import SearchClient, SearchResult


class TavilyClient(SearchClient):
    SEARCH_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str, http=None):
        self._key = api_key
        self._http = http or httpx.Client(timeout=60)
        self._content_cache: dict[str, str] = {}

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        payload = {
            "query": query,
            "max_results": min(limit, 20),
            "include_answer": False,
            "include_raw_content": True,  # full page content, no separate scrape needed
        }
        r = self._http.post(self.SEARCH_URL,
                            headers={"Authorization": f"Bearer {self._key}"},
                            json=payload)
        r.raise_for_status()
        results = []
        for d in r.json().get("results", []):
            url = d["url"]
            raw = d.get("raw_content") or d.get("content", "")
            self._content_cache[url] = raw
            results.append(SearchResult(url=url, title=d.get("title", ""),
                                        snippet=d.get("content", "")))
        return results

    def scrape(self, url: str) -> str:
        # return content already fetched during search; avoids any separate HTTP call
        return self._content_cache.get(url, "")
