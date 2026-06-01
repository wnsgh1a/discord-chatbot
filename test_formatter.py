from formatter import (
    CATEGORY_EMOJIS,
    prioritize_articles,
    split_embed_description,
    truncate,
)


def test_category_emojis_all_present():
    assert CATEGORY_EMOJIS["속보"] == "🚨"
    assert CATEGORY_EMOJIS["이적"] == "🔄"
    assert CATEGORY_EMOJIS["경기"] == "⚽"
    assert CATEGORY_EMOJIS["일반"] == "ℹ️"


def test_truncate_short_text_unchanged():
    assert truncate("hello", 10) == "hello"


def test_truncate_long_text():
    result = truncate("a" * 300, 256)
    assert len(result) == 256
    assert result.endswith("…")


def test_split_embed_description_multiple_chunks():
    text = "line\n" * 2000
    chunks = split_embed_description(text, limit=100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_prioritize_articles_tier1_first():
    articles = [
        {"tier": "일반", "title": "a"},
        {"tier": "⭐최상위", "title": "b"},
        {"tier": "일반", "title": "c"},
        {"tier": "⭐최상위", "title": "d"},
    ]
    result = prioritize_articles(articles, max_count=2)
    assert len(result) == 2
    assert all("⭐" in a["tier"] for a in result)
