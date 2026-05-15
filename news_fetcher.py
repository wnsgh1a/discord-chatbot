import feedparser
import socket
from config import RSS_URLS, MAX_ARTICLES_PER_SOURCE

TIMEOUT_SECONDS = 10
TIER_1_SOURCES = ["Fabrizio Romano", "David Ornstein", "The Athletic", "BBC Sport", "Stone Simon"]


def is_tier1(title: str) -> bool:
    return any(name.lower() in title.lower() for name in TIER_1_SOURCES)


def _parse_feed(url: str) -> str:
    socket.setdefaulttimeout(TIMEOUT_SECONDS)
    feed = feedparser.parse(url)
    if feed.bozo and not feed.entries:
        return ""
    raw = ""
    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        tier_note = "[★1-Tier High Priority★] " if is_tier1(entry.title) else ""
        raw += f"{tier_note}Title: {entry.title}\nLink: {entry.link}\nDate: {entry.published}\n\n"
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
    return combined
