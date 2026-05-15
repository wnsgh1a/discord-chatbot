import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))

RSS_URLS = [
    "https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en",
    "https://www.theguardian.com/football/manchester-united/rss",
    "https://feeds.bbci.co.uk/sport/football/teams/manchester-united/rss.xml",
]

MAX_ARTICLES_PER_SOURCE = 5
DISCORD_MSG_LIMIT = 1900
DEEPSEEK_MODEL = "deepseek-chat"
