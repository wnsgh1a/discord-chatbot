from datetime import datetime
import pytz
import discord

KST = pytz.timezone('Asia/Seoul')

CATEGORY_EMOJIS = {
    "속보": "🚨",
    "이적": "🔄",
    "경기": "⚽",
    "일반": "ℹ️",
}


def build_header() -> str:
    today_kst = datetime.now(KST).strftime('%Y년 %m월 %d일')
    return f"📢 **[{today_kst}] AI 분석: 오늘의 맨유 전문 브리핑 (고도화 버전)**\n\n"


async def send_as_embeds(channel, articles: list[dict]):
    header = build_header()
    await channel.send(header)

    for article in articles:
        emoji = CATEGORY_EMOJIS.get(article["category"], "ℹ️")
        is_tier1 = "⭐" in article["tier"]
        embed_color = 0xFFD700 if is_tier1 else article["color"]

        embed = discord.Embed(
            title=article["title"],
            url=article.get("link"),
            description=article["summary"],
            color=embed_color,
            timestamp=datetime.now(KST),
        )
        embed.set_author(name=f"{emoji} {article['category']}")
        embed.add_field(name="언론사", value=article["source"], inline=True)
        embed.add_field(name="공신력", value=article["tier"], inline=True)
        embed.set_footer(text=f"발행일: {article['date']}")

        await channel.send(embed=embed)
