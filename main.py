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
        raw_news += f"Title: {entry.title}\nLink: {entry.link}\n\n"
    
    prompt = f"다음 뉴스들을 한국어로 요약해줘:\n{raw_news}"
    
    try:
        # 터미널 목록에서 확인된 가장 최신 모델명으로 교체
        response = client.models.generate_content(
            model="models/gemini-2.5-flash", 
            contents=prompt
        )
        
        # 2026년 최신 SDK에서는 response.text로 결과값에 접근합니다.
        await ctx.send(f"📢 **AI 분석: 오늘의 맨유 브리핑**\n\n{response.text}")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        # 아까 429 에러(할당량)가 났으니, 1.5 대신 2.5를 써도 할당량 문제가 생기면 안내합니다.
        if "429" in str(e):
            await ctx.send("⚠️ 2.5 모델 사용량이 일시적으로 초과되었습니다. 1분만 기다려 주세요!")
        else:
            await ctx.send("⚠️ 모델명 연결에 성공했으나 답변 생성 중 문제가 발생했습니다.")

bot.run(os.getenv('DISCORD_TOKEN'))