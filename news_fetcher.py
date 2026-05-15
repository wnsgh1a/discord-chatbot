import feedparser
from config import RSS_URLS, MAX_ARTICLES_PER_SOURCE

# 1티어 공신력 매체
TIER_1_SOURCES = ["Fabrizio Romano", "David Ornstein", "The Athletic", "BBC Sport", "Stone Simon"]


def is_tier1(title: str) -> bool:
    return any(name.lower() in title.lower() for name in TIER_1_SOURCES)


def fetch_news() -> str:
    raw_news = ""
    seen_titles = set()

    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
            if entry.title not in seen_titles:
                tier_note = "[★1-Tier High Priority★] " if is_tier1(entry.title) else ""
                raw_news += f"{tier_note}Title: {entry.title}\nLink: {entry.link}\nDate: {entry.published}\n\n"
                seen_titles.add(entry.title)

    return raw_news
