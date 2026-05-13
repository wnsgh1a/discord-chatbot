import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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

bot.run(os.getenv('DISCORD_TOKEN'))