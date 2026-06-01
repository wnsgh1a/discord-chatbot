import logging
from dataclasses import dataclass

import feedparser
import socket

from config import MAX_ARTICLES_PER_SOURCE, RSS_FETCH_TIMEOUT, RSS_URLS, TIER_1_SOURCES

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = RSS_FETCH_TIMEOUT


@dataclass
class FetchResult:
    match_news: str
    general_news: str

    @property
    def combined(self) -> str:
        return self.match_news + self.general_news

    def has_match_news(self) -> bool:
        return bool(self.match_news.strip())

    @property
    def article_count(self) -> int:
        return self.combined.count("Title:")


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


def _extract_title_from_block(block: str) -> str:
    title_line = [line for line in block.split("\n") if line.startswith("Title:") or "[★1-Tier" in line]
    return title_line[-1].replace("Title: ", "") if title_line else ""


def extract_links_from_raw(raw_news: str) -> list[dict]:
    """RSS 원문 블록에서 제목·링크를 추출합니다 (AI fallback용)."""
    links = []
    for block in raw_news.strip().split("\n\n"):
        if not block.strip():
            continue
        title = _extract_title_from_block(block)
        link = ""
        date = "-"
        for line in block.split("\n"):
            if line.startswith("Link:"):
                link = line.replace("Link:", "").strip()
            elif line.startswith("Date:"):
                date = line.replace("Date:", "").strip()
        if title and link:
            links.append({"title": title, "link": link, "date": date})
    return links


def fetch_news() -> FetchResult:
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
            title = _extract_title_from_block(block)
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            full_block = block + "\n\n"
            if _is_match_result(title):
                match_news += full_block
            else:
                general_news += full_block

    logger.info(
        "뉴스 병합 완료: 경기 %d블록, 일반 %d블록, 중복 제외 후 총 %d건",
        match_news.count("Title:"),
        general_news.count("Title:"),
        (match_news + general_news).count("Title:"),
    )
    return FetchResult(match_news=match_news, general_news=general_news)
