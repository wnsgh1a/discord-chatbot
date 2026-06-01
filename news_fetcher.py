import logging
from dataclasses import dataclass

import feedparser
import requests

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


def is_tier1_text(text: str) -> bool:
    lowered = (text or "").lower()
    return any(name.lower() in lowered for name in TIER_1_SOURCES)


def is_tier1_entry(entry) -> bool:
    parts = [
        getattr(entry, "title", "") or "",
        getattr(entry, "summary", "") or "",
        getattr(entry, "description", "") or "",
        getattr(entry, "author", "") or "",
    ]
    source = getattr(entry, "source", None)
    if source is not None:
        parts.append(getattr(source, "title", "") or "")
        parts.append(getattr(source, "label", "") or "")
    return is_tier1_text(" ".join(parts))


def normalize_title(title: str) -> str:
    from utils import normalize_title as _normalize

    return _normalize(title)


def truncate_raw_news(
    raw_news: str,
    *,
    max_chars: int,
    max_blocks: int,
) -> str:
    blocks = [block for block in raw_news.strip().split("\n\n") if block.strip()]
    if max_blocks > 0:
        blocks = blocks[:max_blocks]
    combined = "\n\n".join(blocks)
    if max_chars > 0 and len(combined) > max_chars:
        combined = combined[:max_chars]
        logger.warning("AI 입력 뉴스 길이 제한 적용: %d자로 잘림", max_chars)
    if max_blocks > 0 and len(blocks) == max_blocks:
        logger.info("AI 입력 뉴스 블록 상한 적용: 최대 %d블록", max_blocks)
    return combined


def _fetch_feed_bytes(url: str) -> bytes | None:
    try:
        response = requests.get(
            url,
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": "ManUtdNewsBot/1.0"},
        )
        response.raise_for_status()
        return response.content
    except requests.Timeout:
        logger.error("RSS 타임아웃 (%ds): %s", TIMEOUT_SECONDS, url)
    except requests.RequestException as exc:
        logger.error("RSS 요청 실패: %s — %s", url, exc)
    return None


def _parse_feed(url: str) -> str:
    content = _fetch_feed_bytes(url)
    if not content:
        return ""

    try:
        feed = feedparser.parse(content)
    except Exception as exc:
        logger.error("RSS 파싱 오류: %s — %s", url, exc)
        return ""

    if feed.bozo and not feed.entries:
        logger.warning("RSS 피드 형식 경고 또는 항목 없음: %s — %s", url, feed.bozo_exception)
        return ""

    raw = ""
    count = min(len(feed.entries), MAX_ARTICLES_PER_SOURCE)
    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        tier_note = "[★1-Tier High Priority★] " if is_tier1_entry(entry) else ""
        title = getattr(entry, "title", "") or "제목 없음"
        link = getattr(entry, "link", "") or ""
        published = getattr(entry, "published", "-")
        raw += f"{tier_note}Title: {title}\nLink: {link}\nDate: {published}\n\n"
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
    seen_keys: set[str] = set()
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
            if not title:
                continue
            dedupe_key = normalize_title(title)
            if dedupe_key in seen_keys:
                logger.debug("중복 제목 제외: %s", title)
                continue
            seen_keys.add(dedupe_key)
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
