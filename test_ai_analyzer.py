from ai_analyzer import (
    build_fallback_articles,
    parse_articles,
    parse_articles_json,
    parse_match_json,
)


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

SAMPLE_JSON = {
    "articles": [
        {
            "category": "일반",
            "source": "BBC Sport",
            "tier": "⭐최상위",
            "title": "맨유, 새 감독 선임 협상 돌입",
            "summary": "맨체스터 유나이티드가 새 감독 선임 협상에 돌입했다.",
            "date": "2025-05-16",
            "link": "https://example.com",
        },
        {
            "category": "이적",
            "source": "Fabrizio Romano",
            "tier": "⭐최상위",
            "title": "산초, 이적 합의 임박",
            "summary": "산초 이적이 임박했다.",
            "date": "2025-05-16",
            "link": "https://example.com/2",
        },
    ]
}


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


def test_parse_articles_json():
    result = parse_articles_json(SAMPLE_JSON)
    assert len(result) == 2
    assert result[0]["title"] == "맨유, 새 감독 선임 협상 돌입"
    assert result[1]["category"] == "이적"
    assert result[1]["color"] == 0xFFD700


def test_parse_articles_json_skips_empty_summary():
    data = {"articles": [{"category": "일반", "summary": "", "title": "X"}]}
    assert parse_articles_json(data) == []


def test_parse_match_json():
    data = {
        "has_match": True,
        "analysis_text": "**경기 요약**\n맨유 2-1 승리",
    }
    result = parse_match_json(data)
    assert result is not None
    assert "경기 요약" in result["text"]


def test_parse_match_json_no_match():
    assert parse_match_json({"has_match": False, "analysis_text": ""}) is None


def test_build_fallback_articles():
    raw = """Title: Man Utd beat Liverpool
Link: https://example.com/match
Date: Mon, 01 Jan 2024

Title: Transfer rumor
Link: https://example.com/transfer
Date: Tue, 02 Jan 2024"""
    result = build_fallback_articles(raw)
    assert len(result) == 2
    assert result[0]["link"] == "https://example.com/match"
    assert "AI 요약에 실패" in result[0]["summary"]
