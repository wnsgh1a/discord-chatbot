import discord
import os
import asyncio
from dotenv import load_dotenv
import feedparser
from google import genai
import re
from datetime import datetime
import pytz

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
KST = pytz.timezone('Asia/Seoul')

# 1티어 공신력 기자/매체 리스트
TIER_1_SOURCES = ["Fabrizio Romano", "David Ornstein", "The Athletic", "BBC Sport", "Stone Simon"]

async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    token = os.getenv('DISCORD_TOKEN')
    channel_id = int(os.getenv('CHANNEL_ID'))

    await bot.login(token)
    channel = await bot.fetch_channel(channel_id)
    
    # 뉴스 소스 리스트 (구글 뉴스, BBC, 가디언)
    rss_urls = [
        "https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en",
        "https://www.theguardian.com/football/manchester-united/rss",
        "https://feeds.bbci.co.uk/sport/football/teams/manchester-united/rss.xml"
    ]
    
    raw_news = ""
    seen_titles = set()
    
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            # 제목 중복 제거
            if entry.title not in seen_titles:
                # 1티어 포함 여부 확인
                is_tier1 = any(name.lower() in entry.title.lower() for name in TIER_1_SOURCES)
                tier_note = "[★1-Tier High Priority★]" if is_tier1 else ""
                
                raw_news += f"{tier_note} Title: {entry.title}\nLink: {entry.link}\nDate: {entry.published}\n\n"
                seen_titles.add(entry.title)

    today_kst = datetime.now(KST).strftime('%Y년 %m월 %d일')
    
    prompt = f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야. 제공된 뉴스들 중 중요한 소식을 골라 한국어로 요약해줘.
특히 '[★1-Tier High Priority★]' 표시가 붙은 기사는 매우 공신력이 높으니 반드시 포함하고 비중 있게 다뤄줘.

결과는 반드시 각 기사마다 아래 형식을 지켜서 '---' 기호로 구분해줘.

[형식]
언론사: [이름]
티어: [공신력 티어 - 1티어인 경우 '⭐최상위'로 표기]
제목: [한글 번역 제목]
내용: [2~3줄 요약]
날짜: [YYYY-MM-DD]
링크: [기사 링크]
---

뉴스 데이터:
{raw_news}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        full_text = response.text
        articles_raw = full_text.split('---')
        
        await channel.send(f"📢 **[{today_kst}] AI 분석: 오늘의 맨유 전문 브리핑 (고도화 버전)**")

        for article in articles_raw:
            if not article.strip() or "내용:" not in article:
                continue
            
            lines = article.strip().split('\n')
            data = {line.split(':', 1).strip(): line.split(':', 1).strip() for line in lines if ':' in line}

            # 1티어 강조 색상 변경 (금색: 0xFFD700, 기본 빨강: 0xDA291C)
            is_star = "⭐" in data.get("티어", "")
            embed_color = 0xFFD700 if is_star else 0xDA291C

            embed = discord.Embed(
                title=data.get("제목", "뉴스 제목"),
                url=data.get("링크", ""),
                description=data.get("내용", "내용 없음"),
                color=embed_color,
                timestamp=datetime.now()
            )
            embed.add_field(name="언론사", value=data.get("언론사", "알 수 없음"), inline=True)
            embed.add_field(name="공신력", value=data.get("티어", "미분류"), inline=True)
            embed.set_footer(text=f"발행일: {data.get('날짜', '-')}")
            
            await channel.send(embed=embed)
            
    except Exception as e:
        await channel.send(f"❌ 에러 발생: {e}")
    
    await bot.close()

if __name__ == "__main__":
    asyncio.run(send_daily_news())