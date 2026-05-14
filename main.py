import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import feedparser
from google import genai

load_dotenv()

# 최신 SDK 설정 방식
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def 뉴스(ctx):
    feed = feedparser.parse("https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en")
    
    raw_news = ""
    for entry in feed.entries[:3]:
        raw_news += f"Title: {entry.title}\nLink: <{entry.link}>\nDate: {entry.published}\n\n"
    
    prompt = f"""
너는 맨체스터 유나이티드 전문 뉴스 분석가야. 아래 뉴스 데이터들을 읽고 다음 형식을 '엄격히' 지켜서 한국어로 출력해줘.

[출력 형식]
번호. **[매체명 / 기자명]** - 공신력 [티어]
(한 줄 띄고)
[요약 내용: 기사의 핵심을 2~3줄로 설명]
(날짜: YYYY-MM-DD 형식)
[기사 읽기](<링크>) 

[주의사항 - 매우 중요!]
1. 링크는 반드시 < > 기호로 감싸서 [기사 읽기](<링크>) 형태로 출력해. 
   - 예시: [기사 읽기](<https://news.google.com/...>)
   - 이렇게 해야 디스코드 미리보기 박스가 생기지 않아.
2. 날짜는 (날짜: 2026-05-13) 처럼 제공된 데이터의 published 날짜를 활용해.

뉴스 데이터:
{raw_news}
"""
    
    try:
        # 터미널 목록에서 확인된 가장 최신 모델명으로 교체
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        # 2026년 최신 SDK에서는 response.text로 결과값에 접근합니다.
        await ctx.send(f"📢 **오늘의 맨유 브리핑**\n\n{response.text}")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        if "429" in str(e):
            await ctx.send("⚠️ 모델 사용량이 일시적으로 초과되었습니다. 1분만 기다려 주세요!")
        else:
            await ctx.send("⚠️ 모델명 연결에 성공했으나 답변 생성 중 문제가 발생했습니다.")

bot.run(os.getenv('DISCORD_TOKEN'))