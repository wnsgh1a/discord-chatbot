from unittest.mock import MagicMock, patch

from news_fetcher import (
    FetchResult,
    extract_links_from_raw,
    fetch_news,
    is_tier1_entry,
    is_tier1_text,
    normalize_title,
    truncate_raw_news,
)


def test_fetch_result_combined():
    result = FetchResult(
        match_news="Title: Match\nLink: http://a.com\nDate: today\n\n",
        general_news="Title: News\nLink: http://b.com\nDate: today\n\n",
    )
    assert result.has_match_news()
    assert result.article_count == 2


def test_normalize_title_dedupes_aliases():
    assert normalize_title("Man Utd sign player") == normalize_title("Manchester United sign player")


def test_truncate_raw_news_limits_blocks():
    blocks = "\n\n".join(f"Title: Article {i}\nLink: http://x.com/{i}\nDate: d" for i in range(10))
    trimmed = truncate_raw_news(blocks, max_chars=10000, max_blocks=3)
    assert trimmed.count("Title:") == 3


def test_extract_links_from_raw():
    raw = """Title: Article One
Link: https://one.example
Date: 2024-01-01

Title: Article Two
Link: https://two.example
Date: 2024-01-02"""
    links = extract_links_from_raw(raw)
    assert len(links) == 2
    assert links[0]["title"] == "Article One"


def test_is_tier1_text():
    assert is_tier1_text("Fabrizio Romano confirms deal")
    assert not is_tier1_text("Random blog post")


def test_is_tier1_entry_uses_source():
    entry = MagicMock(
        title="Transfer news",
        summary="",
        description="",
        author="",
        source=MagicMock(title="Fabrizio Romano", label=""),
    )
    assert is_tier1_entry(entry)


@patch("news_fetcher.RSS_URLS", ["https://example.com/feed"])
@patch("news_fetcher._parse_feed")
def test_fetch_news_deduplicates_by_normalized_title(mock_parse):
    mock_parse.return_value = (
        "Title: Man Utd win\nLink: http://a.com\nDate: d\n\n"
        "Title: Manchester United win\nLink: http://b.com\nDate: d\n\n"
    )
    result = fetch_news()
    assert result.article_count == 1


@patch("news_fetcher.requests.get")
def test_parse_feed_logs_request_failure(mock_get):
    import requests

    from news_fetcher import _parse_feed

    mock_get.side_effect = requests.ConnectionError("network down")
    assert _parse_feed("https://example.com/rss") == ""
