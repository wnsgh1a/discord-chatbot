from ai_analyzer import parse_articles


SAMPLE_ARTICLE = """카테고리: 일반
언론사: BBC Sport
티어: ⭐최상위
제목: 맨유, 새 감독 선임 협상 돌입
내용: 맨체스터 유나이티드가 새 감독 선임을 위한 협상에 돌입했다. 구단 수뇌부는 이번 주 내로 최종 결정을 내릴 예정이다.
날짜: 2025-05-16
링크: https://example.com"""

SAMPLE_TWO_ARTICLES = f"""{SAMPLE_ARTICLE}
---
카테고리: 이적
언론사: Fabrizio Romano
티어: ⭐최상위
제목: 산초, 이적 합의 임박
내용: 제이든 산초의 이적이 임박했다. 개인 조건에 합의했으며 의료 검진만 남은 상태다.
날짜: 2025-05-16
링크: https://example.com/2"""


def test_parse_single_article():
    result = parse_articles(SAMPLE_ARTICLE)
    assert len(result) == 1
    assert result[0]["category"] == "일반"
    assert result[0]["source"] == "BBC Sport"
    assert result[0]["tier"] == "⭐최상위"
    assert "새 감독" in result[0]["title"]


def test_parse_two_articles():
    result = parse_articles(SAMPLE_TWO_ARTICLES)
    assert len(result) == 2
    assert result[0]["category"] == "일반"
    assert result[1]["category"] == "이적"
    assert result[1]["source"] == "Fabrizio Romano"


def test_parse_article_without_content():
    raw = "카테고리: 일반\n언론사: Test\n"
    result = parse_articles(raw)
    assert len(result) == 0


def test_parse_article_fallback_category():
    raw = """언론사: Test
티어: 일반
제목: Test Title
내용: Test content
날짜: 2025-01-01
링크: https://example.com"""
    result = parse_articles(raw)
    assert len(result) == 1
    assert result[0]["category"] == "일반"


def test_tier1_color():
    result = parse_articles(SAMPLE_ARTICLE)
    assert result[0]["color"] == 0xFFD700
