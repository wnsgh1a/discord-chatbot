import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import feedparser

load_dotenv()

# 맨유 뉴스 RSS 주소 (영문 검색 결과)
RSS_URL = "https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en"

# 봇 권한 및 접두사 설정
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# 봇 실행 확인용 이벤트
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# 테스트 명령어: !안녕
@bot.command()
async def 안녕(ctx):
    await ctx.send('Hello World! 맨유 봇 가동 준비 완료!')

# 추가된 뉴스 기능
@bot.command()
async def 뉴스(ctx):
    feed = feedparser.parse(RSS_URL)
    
    news_list = []
    for entry in feed.entries[:3]:
        title = entry.title[:100] + "..." if len(entry.title) > 100 else entry.title
        news_list.append(f"🔹 **{title}**\n<{entry.link}>")
    
    result = "\n\n".join(news_list)
    
    if len(result) > 1900:
        result = result[:1900] + "\n... (내용이 너무 길어 생략되었습니다)"

    await ctx.send(f"🔴 **맨체스터 유나이티드 최신 뉴스 (24시간)**\n\n{result}")

bot.run(os.getenv('DISCORD_TOKEN'))