import argparse
import asyncio
import logging

import aiohttp
import discord
from discord import Webhook

from article_store import record_sent_urls
from briefing import build_briefing
from config import (
    DISCORD_TOKEN,
    DISCORD_WEBHOOK_URL,
    ConfigError,
    get_channel_id,
    is_dry_run_env,
    use_discord_webhook,
    validate_config,
)
from dry_run_output import print_briefing, save_briefing_json
from logging_config import setup_logging
import formatter

logger = logging.getLogger(__name__)


async def deliver_to_channel(channel, result, *, record_sent: bool = True) -> None:
    if result.empty_message:
        await channel.send(result.empty_message)
        return

    logger.info(
        "전송 준비: 기사 %d건 (fallback=%s, 중복제외=%d)",
        len(result.articles),
        result.fallback_mode,
        result.skipped_count,
    )
    sent_urls = await formatter.send_as_embeds(
        channel,
        result.articles,
        result.match_analysis,
        fallback_mode=result.fallback_mode,
    )
    if record_sent and sent_urls:
        record_sent_urls(sent_urls)


async def deliver_via_webhook(webhook_url: str, result) -> None:
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await deliver_to_channel(webhook, result)


async def deliver_via_bot(result) -> None:
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)
    channel_id = get_channel_id()

    logger.info("Discord 로그인 시도 (channel_id=%s)", channel_id)
    try:
        await bot.login(DISCORD_TOKEN)
        channel = await bot.fetch_channel(channel_id)
    except discord.LoginFailure:
        logger.error("Discord 로그인 실패: 토큰을 확인하세요")
        await bot.close()
        raise
    except discord.NotFound:
        logger.error("채널을 찾을 수 없음: channel_id=%s", channel_id)
        await bot.close()
        raise

    logger.info("채널 연결 완료: %s", channel_id)
    try:
        await deliver_to_channel(channel, result)
        logger.info("Discord 전송 완료")
    except discord.Forbidden:
        logger.error("채널 메시지 전송 권한 없음")
        await channel.send("❌ 봇에 채널 메시지 전송 권한이 없습니다.")
    except Exception as e:
        logger.exception("일일 뉴스 전송 중 오류")
        await channel.send(f"❌ 에러 발생: {e}")
    finally:
        await bot.close()


async def run_daily_news(*, dry_run: bool = False, output_path: str | None = None) -> None:
    webhook_mode = use_discord_webhook()
    validate_config(dry_run=dry_run, webhook=webhook_mode and not dry_run)

    result = build_briefing()

    if dry_run:
        print_briefing(result)
        if output_path or not result.empty_message:
            path = save_briefing_json(result, output_path)
            print(f"JSON 저장: {path}")
        return

    if webhook_mode:
        logger.info("Discord Webhook으로 전송")
        await deliver_via_webhook(DISCORD_WEBHOOK_URL, result)
        return

    await deliver_via_bot(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manchester United Daily News Bot")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discord 전송 없이 콘솔에 브리핑 출력",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="dry-run 시 JSON 저장 경로 (기본: data/dry_run_briefing.json)",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()
    dry_run = args.dry_run or is_dry_run_env()

    try:
        asyncio.run(run_daily_news(dry_run=dry_run, output_path=args.output))
    except ConfigError as e:
        logger.error("%s", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
