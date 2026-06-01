import logging
from dataclasses import dataclass

from ai_analyzer import analyze_match, analyze_news, build_fallback_articles
from article_store import filter_new_articles
from news_fetcher import fetch_news

logger = logging.getLogger(__name__)


@dataclass
class BriefingResult:
    articles: list[dict]
    match_analysis: dict | None
    fallback_mode: bool
    skipped_count: int
    article_count: int
    empty_message: str | None = None


def build_briefing() -> BriefingResult:
    fetched = fetch_news()
    if not fetched.combined:
        logger.warning("수집된 뉴스 없음")
        return BriefingResult(
            articles=[],
            match_analysis=None,
            fallback_mode=False,
            skipped_count=0,
            article_count=0,
            empty_message="❌ 뉴스를 가져오지 못했습니다. RSS 피드를 확인해주세요.",
        )

    logger.info("수집된 뉴스 블록 수: %d", fetched.article_count)

    match_analysis = None
    if fetched.has_match_news():
        logger.info("경기 분석 시작 (경기 뉴스 %d블록)", fetched.match_news.count("Title:"))
        match_analysis = analyze_match(fetched.match_news)

    logger.info("AI 뉴스 분석 시작")
    articles = analyze_news(fetched.combined)
    fallback_mode = False
    if not articles:
        logger.warning("AI 요약 실패, 원문 링크 fallback 사용")
        articles = build_fallback_articles(fetched.combined)
        fallback_mode = True

    articles, skipped_count = filter_new_articles(articles)
    empty_message = None
    if not articles and not match_analysis:
        if skipped_count:
            empty_message = (
                "📭 오늘 수집된 뉴스는 모두 이전에 전송한 기사입니다. 새 소식이 없습니다."
            )
        else:
            empty_message = "❌ 표시할 뉴스가 없습니다."

    return BriefingResult(
        articles=articles,
        match_analysis=match_analysis,
        fallback_mode=fallback_mode,
        skipped_count=skipped_count,
        article_count=fetched.article_count,
        empty_message=empty_message,
    )
