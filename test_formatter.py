from datetime import datetime
import pytz
from formatter import build_header, CATEGORY_EMOJIS


def test_build_header_contains_date():
    header = build_header()
    KST = pytz.timezone('Asia/Seoul')
    today = datetime.now(KST).strftime('%Y년 %m월 %d일')
    assert today in header
    assert "맨유" in header and "브리핑" in header


def test_category_emojis_all_present():
    assert CATEGORY_EMOJIS["속보"] == "🚨"
    assert CATEGORY_EMOJIS["이적"] == "🔄"
    assert CATEGORY_EMOJIS["경기"] == "⚽"
    assert CATEGORY_EMOJIS["일반"] == "ℹ️"
