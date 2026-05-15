import asyncio
import discord
from config import DISCORD_TOKEN, CHANNEL_ID
from news_fetcher import fetch_news
from ai_analyzer import analyze_news
import formatter


async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    await bot.login(DISCORD_TOKEN)
    channel = await bot.fetch_channel(CHANNEL_ID)

    try:
        raw_news = fetch_news()
        if not raw_news:
            await channel.send("❌ 뉴스를 가져오지 못했습니다.")
            await bot.close()
            return

        articles = analyze_news(raw_news)

        await formatter.send_as_embeds(channel, articles)

    except Exception as e:
        await channel.send(f"❌ 에러 발생: {e}")

    await bot.close()


if __name__ == "__main__":
    asyncio.run(send_daily_news())
