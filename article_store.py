import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pytz

from config import SENT_URL_RETENTION_DAYS, SENT_URLS_PATH

logger = logging.getLogger(__name__)
KST = pytz.timezone("Asia/Seoul")


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def _load_store(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {normalize_url(k): v for k, v in data.items() if k}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("전송 기록 로드 실패, 새로 시작: %s", e)
    return {}


def _save_store(path: Path, store: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def prune_store(store: dict[str, str], retention_days: int) -> dict[str, str]:
    if retention_days <= 0:
        return store
    cutoff = datetime.now(KST) - timedelta(days=retention_days)
    pruned = {}
    for url, sent_at in store.items():
        try:
            dt = datetime.fromisoformat(sent_at)
            if dt.tzinfo is None:
                dt = KST.localize(dt)
        except ValueError:
            continue
        if dt >= cutoff:
            pruned[url] = sent_at
    removed = len(store) - len(pruned)
    if removed:
        logger.info("만료된 전송 기록 %d건 삭제", removed)
    return pruned


def filter_new_articles(
    articles: list[dict],
    path: str | Path | None = None,
    retention_days: int | None = None,
) -> tuple[list[dict], int]:
    """이미 전송한 URL을 제외한 기사 목록과 제외 건수를 반환합니다."""
    store_path = Path(path or SENT_URLS_PATH)
    retention = retention_days if retention_days is not None else SENT_URL_RETENTION_DAYS
    store = prune_store(_load_store(store_path), retention)

    new_articles = []
    skipped = 0
    for article in articles:
        link = normalize_url(article.get("link", ""))
        if link and link in store:
            skipped += 1
            continue
        new_articles.append(article)

    if skipped:
        logger.info("이미 전송한 URL %d건 제외", skipped)
    return new_articles, skipped


def record_sent_urls(
    urls: list[str],
    path: str | Path | None = None,
    retention_days: int | None = None,
) -> None:
    store_path = Path(path or SENT_URLS_PATH)
    retention = retention_days if retention_days is not None else SENT_URL_RETENTION_DAYS
    store = prune_store(_load_store(store_path), retention)
    now = datetime.now(KST).isoformat()
    for url in urls:
        normalized = normalize_url(url)
        if normalized:
            store[normalized] = now
    _save_store(store_path, store)
    logger.info("전송 URL %d건 기록 저장: %s", len(urls), store_path)
