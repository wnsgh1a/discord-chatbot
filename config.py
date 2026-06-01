import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0") or "0")

RSS_URLS = [
    "https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en",
    "https://www.theguardian.com/football/manchester-united/rss",
    "https://feeds.bbci.co.uk/sport/football/teams/manchester-united/rss.xml",
]

MAX_ARTICLES_PER_SOURCE = 5
DISCORD_MSG_LIMIT = 1900
DEEPSEEK_MODEL = "deepseek-chat"


class ConfigError(ValueError):
    """필수 환경 변수가 없거나 잘못되었을 때 발생합니다."""


def validate_config(
    discord_token: str | None = None,
    deepseek_api_key: str | None = None,
    channel_id: int | None = None,
) -> None:
    token = discord_token if discord_token is not None else DISCORD_TOKEN
    api_key = deepseek_api_key if deepseek_api_key is not None else DEEPSEEK_API_KEY
    ch_id = channel_id if channel_id is not None else CHANNEL_ID

    missing = []
    if not token or not str(token).strip():
        missing.append("DISCORD_TOKEN")
    if not api_key or not str(api_key).strip():
        missing.append("DEEPSEEK_API_KEY")
    if not ch_id or ch_id <= 0:
        missing.append("CHANNEL_ID (양의 정수 Discord 채널 ID)")

    if missing:
        raise ConfigError(
            "필수 환경 변수가 설정되지 않았습니다: "
            + ", ".join(missing)
            + ". .env 파일 또는 GitHub Secrets를 확인하세요."
        )
