from news_fetcher import FetchResult, extract_links_from_raw


def test_fetch_result_combined():
    result = FetchResult(
        match_news="Title: Match\nLink: http://a.com\nDate: today\n\n",
        general_news="Title: News\nLink: http://b.com\nDate: today\n\n",
    )
    assert result.has_match_news()
    assert result.article_count == 2
    assert "Match" in result.combined


def test_fetch_result_no_match():
    result = FetchResult(match_news="", general_news="Title: Only\nLink: http://x.com\nDate: d\n\n")
    assert not result.has_match_news()
    assert result.article_count == 1


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
    assert links[1]["link"] == "https://two.example"
