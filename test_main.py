from unittest.mock import AsyncMock, patch

import pytest

from briefing import BriefingResult
from main import deliver_to_channel, run_daily_news


@pytest.mark.asyncio
@patch("main.build_briefing")
@patch("main.validate_config")
async def test_run_daily_news_dry_run(mock_validate, mock_build):
    mock_build.return_value = BriefingResult(
        articles=[],
        match_analysis=None,
        fallback_mode=False,
        skipped_count=0,
        article_count=0,
        empty_message="empty",
    )
    await run_daily_news(dry_run=True)
    mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_deliver_empty_message():
    channel = AsyncMock()
    result = BriefingResult(
        articles=[],
        match_analysis=None,
        fallback_mode=False,
        skipped_count=0,
        article_count=0,
        empty_message="📭 없음",
    )
    await deliver_to_channel(channel, result, record_sent=False)
    channel.send.assert_awaited_once_with("📭 없음")
