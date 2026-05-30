import httpx
from .base import SearchClient, SearchResult


class FirecrawlClient(SearchClient):
    BASE = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: str, http=None):
        self._key = api_key
        self._http = http or httpx.Client(timeout=60)

    def _headers(self):
        return {"Authorization": f"Bearer {self._key}"}

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        r = self._http.post(f"{self.BASE}/search",
                            headers=self._headers(),
                            json={"query": query, "limit": limit})
        r.raise_for_status()
        return [SearchResult(url=d["url"], title=d.get("title", ""),
                             snippet=d.get("description", ""))
                for d in r.json().get("data", [])]

    def scrape(self, url: str) -> str:
        r = self._http.post(f"{self.BASE}/scrape",
                            headers=self._headers(),
                            json={"url": url, "formats": ["markdown"]})
        r.raise_for_status()
        return r.json().get("data", {}).get("markdown", "")
