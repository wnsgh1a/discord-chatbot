from unittest.mock import patch

import pytest

from ai_analyzer import (
    AIAnalysisError,
    analyze_news,
    build_fallback_articles,
    parse_articles,
    parse_articles_json,
    parse_match_json,
)

SAMPLE_ARTICLE = """카테고리: 일반
언론사: BBC Sport
티어: ⭐최상위
제목: 맨유, 새 감독 선임 협상 돌입
내용: 맨체스터 유나이티드가 새 감독 선임을 위한 협상에 돌입했다.
날짜: 2025-05-16
링크: https://example.com"""

SAMPLE_JSON = {
    "articles": [
        {
            "category": "일반",
            "source": "BBC Sport",
            "tier": "⭐최상위",
            "title": "맨유, 새 감독 선임 협상 돌입",
            "summary": "협상에 돌입했다.",
            "date": "2025-05-16",
            "link": "https://example.com",
        }
    ]
}


def test_parse_single_article():
    result = parse_articles(SAMPLE_ARTICLE)
    assert len(result) == 1
    assert "새 감독" in result[0]["title"]


def test_parse_articles_json():
    result = parse_articles_json(SAMPLE_JSON)
    assert len(result) == 1
    assert result[0]["color"] == 0xFFD700


def test_parse_match_json():
    data = {"has_match": True, "analysis_text": "**경기 요약**\n맨유 2-1 승리"}
    result = parse_match_json(data)
    assert result is not None


def test_build_fallback_articles():
    raw = "Title: Test\nLink: https://example.com/x\nDate: Mon\n\n"
    result = build_fallback_articles(raw)
    assert len(result) == 1
    assert "AI 요약에 실패" in result[0]["summary"]


@patch("ai_analyzer._call_api_json")
def test_analyze_news_success(mock_api):
    mock_api.return_value = SAMPLE_JSON
    articles = analyze_news("Title: x\nLink: http://a.com\nDate: d\n\n")
    assert len(articles) == 1


@patch("ai_analyzer._call_api_json")
def test_analyze_news_raises_ai_error(mock_api):
    mock_api.side_effect = AIAnalysisError("테스트 실패")
    with pytest.raises(AIAnalysisError):
        analyze_news("Title: x\nLink: http://a.com\nDate: d\n\n")
