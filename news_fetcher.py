import logging
import feedparser
import socket

from config import MAX_ARTICLES_PER_SOURCE, RSS_URLS

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10
TIER_1_SOURCES = ["Fabrizio Romano", "David Ornstein", "The Athletic", "BBC Sport", "Stone Simon"]


def is_tier1(title: str) -> bool:
    return any(name.lower() in title.lower() for name in TIER_1_SOURCES)


def _parse_feed(url: str) -> str:
    socket.setdefaulttimeout(TIMEOUT_SECONDS)
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        logger.warning("RSS 피드 파싱 실패 또는 항목 없음: %s", url)
        return ""
    raw = ""
    count = min(len(feed.entries), MAX_ARTICLES_PER_SOURCE)
    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        tier_note = "[★1-Tier High Priority★] " if is_tier1(entry.title) else ""
        raw += f"{tier_note}Title: {entry.title}\nLink: {entry.link}\nDate: {entry.published}\n\n"
    logger.info("RSS 수집 완료: %s (%d건)", url, count)
    return raw


MATCH_KEYWORDS = [
    "win", "loss", "draw", "beat", "defeat", "victory", "result", "highlight",
    "match report", "player ratings", "premier league", "fa cup", "europa league",
    "carabao cup", "champions league",
]


def _is_match_result(title: str) -> bool:
    return any(kw in title.lower() for kw in MATCH_KEYWORDS)


def fetch_news() -> str:
    seen_titles = set()
    match_news = ""
    general_news = ""

    for url in RSS_URLS:
        raw = _parse_feed(url)
        if not raw:
            continue
        for block in raw.strip().split("\n\n"):
            if not block:
                continue
            title_line = [l for l in block.split("\n") if l.startswith("Title:") or "[★1-Tier" in l]
            title = title_line[-1].replace("Title: ", "") if title_line else ""
            if title in seen_titles:
                continue
            seen_titles.add(title)
            full_block = block + "\n\n"
            if _is_match_result(title):
                match_news += full_block
            else:
                general_news += full_block

    combined = match_news + general_news
    logger.info(
        "뉴스 병합 완료: 경기 %d블록, 일반 %d블록, 중복 제외 후 총 %d건",
        match_news.count("Title:"),
        general_news.count("Title:"),
        combined.count("Title:"),
    )
    return combined
