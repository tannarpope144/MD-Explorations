import pytest
from evaluate.stages.context import ResearchContext, SearchBudgetExceeded


class FakeSearch:
    def __init__(self): self.n = 0
    def search(self, q, limit=10): self.n += 1; return []
    def scrape(self, url): return "md"


def test_search_increments_and_enforces_budget():
    ctx = ResearchContext(search=FakeSearch(), llm_for=lambda c: (None, "m"),
                          max_searches=2)
    ctx.search("a"); ctx.search("b")
    with pytest.raises(SearchBudgetExceeded):
        ctx.search("c")


def test_searches_used_tracked():
    ctx = ResearchContext(search=FakeSearch(), llm_for=lambda c: (None, "m"),
                          max_searches=5)
    ctx.search("a")
    assert ctx.searches_used == 1
