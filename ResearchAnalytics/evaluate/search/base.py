from abc import ABC, abstractmethod
from pydantic import BaseModel


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str = ""


class SearchClient(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]: ...

    @abstractmethod
    def scrape(self, url: str) -> str: ...
