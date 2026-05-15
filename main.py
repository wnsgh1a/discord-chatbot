import asyncio
import discord
from config import DISCORD_TOKEN, CHANNEL_ID
from news_fetcher import fetch_news
from ai_analyzer import analyze_news, analyze_match
import formatter


async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    await bot.login(DISCORD_TOKEN)
    channel = await bot.fetch_channel(CHANNEL_ID)

    try:
        raw_news = fetch_news()
        if not raw_news:
            await channel.send("❌ 뉴스를 가져오지 못했습니다. RSS 피드를 확인해주세요.")
            await bot.close()
            return

        # 경기 분석 (있으면 먼저 출력, 없으면 None)
        match_analysis = analyze_match(raw_news) if "경기" in raw_news or any(
            kw in raw_news.lower() for kw in ["result", "match report", "premier league"]
        ) else None

        # 일반 뉴스 분석
        articles = analyze_news(raw_news)

        await formatter.send_as_embeds(channel, articles, match_analysis)

    except discord.Forbidden:
        await channel.send("❌ 봇에 채널 메시지 전송 권한이 없습니다.")
    except discord.NotFound:
        await channel.send("❌ 채널을 찾을 수 없습니다. CHANNEL_ID를 확인해주세요.")
    except discord.LoginFailure:
        await channel.send("❌ Discord 로그인에 실패했습니다. 토큰을 확인해주세요.")
    except Exception as e:
        await channel.send(f"❌ 에러 발생: {e}")

    await bot.close()


if __name__ == "__main__":
    asyncio.run(send_daily_news())
