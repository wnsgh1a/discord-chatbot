from datetime import datetime
import pytz
from formatter import CATEGORY_EMOJIS


def test_category_emojis_all_present():
    assert CATEGORY_EMOJIS["속보"] == "🚨"
    assert CATEGORY_EMOJIS["이적"] == "🔄"
    assert CATEGORY_EMOJIS["경기"] == "⚽"
    assert CATEGORY_EMOJIS["일반"] == "ℹ️"
