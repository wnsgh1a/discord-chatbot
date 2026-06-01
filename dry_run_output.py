import json
import logging
from pathlib import Path

from briefing import BriefingResult
from config import DRY_RUN_OUTPUT_PATH
from formatter import prioritize_articles

logger = logging.getLogger(__name__)


def _serialize_result(result: BriefingResult) -> dict:
    articles = prioritize_articles(list(result.articles))
    return {
        "article_count_collected": result.article_count,
        "articles_to_send": len(articles),
        "skipped_duplicates": result.skipped_count,
        "fallback_mode": result.fallback_mode,
        "empty_message": result.empty_message,
        "match_analysis": result.match_analysis,
        "articles": articles,
    }


def print_briefing(result: BriefingResult) -> None:
    print("\n" + "=" * 60)
    print("  DRY RUN — Manchester United Daily News Bot")
    print("=" * 60)

    if result.empty_message:
        print(f"\n{result.empty_message}\n")
        return

    print(f"\n수집: {result.article_count}블록 | 중복 제외: {result.skipped_count}건")
    print(f"fallback 모드: {result.fallback_mode}")

    if result.match_analysis:
        print("\n--- 경기 분석 ---")
        print(result.match_analysis.get("text", ""))

    articles = prioritize_articles(list(result.articles))
    print(f"\n--- 기사 ({len(articles)}건) ---")
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}] {article.get('category')} | {article.get('tier')}")
        print(f"제목: {article.get('title')}")
        print(f"언론사: {article.get('source')}")
        print(f"요약: {article.get('summary')}")
        print(f"링크: {article.get('link')}")
        print(f"날짜: {article.get('date')}")

    print("\n" + "=" * 60)
    print("  (Discord 전송·URL 기록 없음)")
    print("=" * 60 + "\n")


def save_briefing_json(result: BriefingResult, path: str | Path | None = None) -> Path:
    out_path = Path(path or DRY_RUN_OUTPUT_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _serialize_result(result)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("dry-run 결과 저장: %s", out_path)
    return out_path
