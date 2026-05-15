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

async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    token = os.getenv('DISCORD_TOKEN')
    channel_id = int(os.getenv('CHANNEL_ID'))

    await bot.login(token)
    channel = await bot.fetch_channel(channel_id)
    
    feed = feedparser.parse("https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en")
    
    raw_news = ""
    for entry in feed.entries[:10]:
        raw_news += f"Title: {entry.title}\nLink: {entry.link}\nDate: {entry.published}\n\n"
    
    today_kst = datetime.now(KST).strftime('%Y년 %m월 %d일')
    
    prompt = f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야. 아래 뉴스 데이터들을 읽고 한국어로 요약해줘.
결과는 반드시 각 기사마다 아래 형식을 지켜서 구분해줘. '---' 기호로 기사를 구분해.

[형식]
언론사: [이름]
티어: [공신력 티어]
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
        
        await channel.send(f"📢 **[{today_kst}] AI 분석: 오늘의 맨유 브리핑**")

        for article in articles_raw:
            if not article.strip() or "내용:" not in article:
                continue
            
            lines = article.strip().split('\n')
            data = {}
            for line in lines:
                if ':' in line:
                    key, val = line.split(':', 1)
                    data[key.strip()] = val.strip()

            embed = discord.Embed(
                title=data.get("제목", "뉴스 제목"),
                url=data.get("링크", ""),
                description=data.get("내용", "내용 없음"),
                color=0xDA291C, # 맨유 상징색 (Red)
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