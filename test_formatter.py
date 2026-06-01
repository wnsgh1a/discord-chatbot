from formatter import (
    CATEGORY_EMOJIS,
    _build_category_digest_embed,
    prioritize_articles,
    split_embed_description,
    truncate,
)


def test_category_emojis_all_present():
    assert CATEGORY_EMOJIS["속보"] == "🚨"
    assert CATEGORY_EMOJIS["이적"] == "🔄"
    assert CATEGORY_EMOJIS["경기"] == "⚽"
    assert CATEGORY_EMOJIS["일반"] == "ℹ️"


def test_truncate_long_text():
    result = truncate("a" * 300, 256)
    assert len(result) == 256
    assert result.endswith("…")


def test_split_embed_description_multiple_chunks():
    text = "line\n" * 2000
    chunks = split_embed_description(text, limit=100)
    assert len(chunks) > 1


def test_prioritize_articles_tier1_first():
    articles = [
        {"tier": "일반", "title": "a"},
        {"tier": "⭐최상위", "title": "b"},
    ]
    result = prioritize_articles(articles, max_count=1)
    assert result[0]["title"] == "b"


def test_build_category_digest_embed():
    articles = [
        {
            "category": "이적",
            "color": 0xFF8800,
            "title": "Test",
            "summary": "Summary text",
            "link": "https://example.com",
        }
    ]
    embed = _build_category_digest_embed("이적", articles)
    assert "이적" in embed.title
    assert "Test" in embed.description
