import asyncio
import logging

import discord

from article_store import filter_new_articles, record_sent_urls
from config import CHANNEL_ID, DISCORD_TOKEN, ConfigError, validate_config
from logging_config import setup_logging
from news_fetcher import fetch_news
from ai_analyzer import analyze_news, analyze_match, build_fallback_articles
import formatter

logger = logging.getLogger(__name__)


async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    logger.info("Discord 로그인 시도")
    try:
        await bot.login(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Discord 로그인 실패: 토큰을 확인하세요")
        raise

    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
    except discord.NotFound:
        logger.error("채널을 찾을 수 없음: CHANNEL_ID=%s", CHANNEL_ID)
        await bot.close()
        raise
    except discord.HTTPException as e:
        logger.error("채널 조회 실패: %s", e)
        await bot.close()
        raise

    logger.info("채널 연결 완료: %s", CHANNEL_ID)

    try:
        logger.info("RSS 뉴스 수집 시작")
        fetched = fetch_news()
        if not fetched.combined:
            logger.warning("수집된 뉴스 없음")
            await channel.send("❌ 뉴스를 가져오지 못했습니다. RSS 피드를 확인해주세요.")
            return

        logger.info("수집된 뉴스 블록 수: %d", fetched.article_count)

        match_analysis = None
        if fetched.has_match_news():
            logger.info("경기 분석 시작 (경기 뉴스 %d블록)", fetched.match_news.count("Title:"))
            match_analysis = analyze_match(fetched.match_news)

        logger.info("AI 뉴스 분석 시작")
        articles = analyze_news(fetched.combined)
        use_fallback = False
        if not articles:
            logger.warning("AI 요약 실패, 원문 링크 fallback 사용")
            articles = build_fallback_articles(fetched.combined)
            use_fallback = True

        articles, skipped_count = filter_new_articles(articles)
        if not articles and not match_analysis:
            if skipped_count:
                await channel.send(
                    "📭 오늘 수집된 뉴스는 모두 이전에 전송한 기사입니다. 새 소식이 없습니다."
                )
            else:
                await channel.send("❌ 표시할 뉴스가 없습니다.")
            return

        logger.info(
            "전송 준비: 기사 %d건 (fallback=%s, 중복제외=%d)",
            len(articles),
            use_fallback,
            skipped_count,
        )
        sent_urls = await formatter.send_as_embeds(
            channel, articles, match_analysis, fallback_mode=use_fallback
        )
        if sent_urls:
            record_sent_urls(sent_urls)
        logger.info("Discord 전송 완료")

    except discord.Forbidden:
        logger.error("채널 메시지 전송 권한 없음")
        await channel.send("❌ 봇에 채널 메시지 전송 권한이 없습니다.")
    except Exception as e:
        logger.exception("일일 뉴스 전송 중 오류")
        await channel.send(f"❌ 에러 발생: {e}")
    finally:
        await bot.close()


def main() -> None:
    setup_logging()
    try:
        validate_config()
    except ConfigError as e:
        logger.error("%s", e)
        raise SystemExit(1) from e
    asyncio.run(send_daily_news())


if __name__ == "__main__":
    main()
