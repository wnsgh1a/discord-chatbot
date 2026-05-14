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

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

async def send_daily_news():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    # 환경 변수에서 채널 ID와 토큰을 가져옵니다.
    token = os.getenv('DISCORD_TOKEN')
    channel_id = int(os.getenv('CHANNEL_ID'))

    await bot.login(token)
    
    channel = await bot.fetch_channel(channel_id)
    
    # 1. 뉴스 가져오기
    feed = feedparser.parse("https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en")
    
    raw_news = ""
    for entry in feed.entries[:10]:
        raw_news += f"Title: {entry.title}\nLink: <{entry.link}>\nDate: {entry.published}\n\n"
    
    # 2. 한국 날짜 생성
    today_kst = datetime.now(KST).strftime('%Y년 %m월 %d일')
    
    prompt = f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야. 아래 뉴스 데이터들을 읽고 다음 형식을 '엄격히' 지켜서 한국어로 출력해줘.

[출력 형식]
번호. **[언론사 정보]** - 공신력 [티어]
기사 핵심 내용을 2~3줄로 요약하여 설명.
(날짜: YYYY-MM-DD)

[기사 읽기](<링크>)

[언론사 정보 표기 규칙]
1. 언론사 이름만 알 수 있는 경우: [언론사 이름]
2. 기자 이름까지 알 수 있는 경우: [언론사 이름 - 기자 이름]
   - 주의: "/" 기호는 사용하지 마.

[주의사항]
1. 각 기사의 시작은 반드시 '번호.' 형태로 시작해.
2. '[요약 내용: ...]' 같은 가이드 문구는 절대 포함하지 말고 바로 요약 본문을 작성해.
3. '(날짜: ...)' 출력 후 반드시 한 줄을 띄우고 그 다음 줄에 '[기사 읽기](<링크>)'를 작성해.
4. 링크는 반드시 < > 기호로 감싸서 [기사 읽기](<링크>) 형태로 출력해.

뉴스 데이터:
{raw_news}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        full_text = response.text
        articles = [a.strip() for a in re.split(r'\n(?=\d+\.)', full_text.strip()) if a.strip()]
        
        header = f"📢 **[{today_kst}] AI 분석: 오늘의 맨유 브리핑**\n\n"
        current_message = header
        
        for article in articles:
            if len(current_message) + len(article) + 2 > 1900:
                await channel.send(current_message)
                current_message = article + "\n\n"
            else:
                current_message += article + "\n\n"
        
        if current_message:
            await channel.send(current_message)
            
    except Exception as e:
        await channel.send(f"❌ 에러 발생: {e}")
    
    await bot.close()

if __name__ == "__main__":
    asyncio.run(send_daily_news())