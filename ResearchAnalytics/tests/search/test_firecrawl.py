from evaluate.search.base import SearchResult
from evaluate.search.firecrawl import FirecrawlClient


def test_search_parses_results(mocker):
    http = mocker.Mock()
    resp = mocker.Mock()
    resp.json.return_value = {"data": [
        {"url": "https://a.com", "title": "A", "description": "d"},
    ]}
    resp.raise_for_status = mocker.Mock()
    http.post.return_value = resp
    c = FirecrawlClient(api_key="k", http=http)
    out = c.search("ubi finland", limit=5)
    assert out[0].url == "https://a.com" and isinstance(out[0], SearchResult)


def test_scrape_returns_markdown(mocker):
    http = mocker.Mock()
    resp = mocker.Mock()
    resp.json.return_value = {"data": {"markdown": "# hello"}}
    resp.raise_for_status = mocker.Mock()
    http.post.return_value = resp
    c = FirecrawlClient(api_key="k", http=http)
    md = c.scrape("https://a.com")
    assert md == "# hello"
