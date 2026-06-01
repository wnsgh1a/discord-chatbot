from datetime import datetime, timedelta

import pytz

from article_store import (
    filter_new_articles,
    normalize_url,
    prune_store,
    record_sent_urls,
)

KST = pytz.timezone("Asia/Seoul")


def test_normalize_url_strips_trailing_slash():
    assert normalize_url("https://Example.COM/news/") == normalize_url("https://example.com/news")


def test_filter_new_articles_excludes_seen(tmp_path):
    path = tmp_path / "sent_urls.json"
    articles = [
        {"title": "A", "link": "https://example.com/a", "summary": "s"},
        {"title": "B", "link": "https://example.com/b", "summary": "s"},
    ]
    new, skipped = filter_new_articles(articles, path=path, retention_days=7)
    assert len(new) == 2
    assert skipped == 0

    record_sent_urls(["https://example.com/a"], path=path)
    new, skipped = filter_new_articles(articles, path=path, retention_days=7)
    assert len(new) == 1
    assert new[0]["link"] == "https://example.com/b"
    assert skipped == 1


def test_prune_store_removes_old_entries():
    old = (datetime.now(KST) - timedelta(days=10)).isoformat()
    recent = datetime.now(KST).isoformat()
    store = {
        "https://example.com/old": old,
        "https://example.com/new": recent,
    }
    pruned = prune_store(store, retention_days=7)
    assert "https://example.com/old" not in pruned
    assert "https://example.com/new" in pruned
