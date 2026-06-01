import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0") or "0")
TEST_CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID", "0") or "0")
DISCORD_WEBHOOK_URL = (os.getenv("DISCORD_WEBHOOK_URL") or "").strip()

DEFAULT_RSS_URLS = [
    "https://news.google.com/rss/search?q=Manchester+United+when:24h&hl=en-US&gl=US&ceid=US:en",
    "https://www.theguardian.com/football/manchester-united/rss",
    "https://feeds.bbci.co.uk/sport/football/teams/manchester-united/rss.xml",
]

DEFAULT_TIER_1_SOURCES = [
    "Fabrizio Romano",
    "David Ornstein",
    "The Athletic",
    "BBC Sport",
    "Stone Simon",
]

DISCORD_MSG_LIMIT = 1900
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SENT_URLS_PATH = os.getenv("SENT_URLS_PATH", "data/sent_urls.json")
SENT_URL_RETENTION_DAYS = int(os.getenv("SENT_URL_RETENTION_DAYS", "7"))
MAX_EMBEDS_PER_RUN = int(os.getenv("MAX_EMBEDS_PER_RUN", "15"))
EMBED_SEND_DELAY_SEC = float(os.getenv("EMBED_SEND_DELAY_SEC", "0.6"))
MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "5"))
RSS_FETCH_TIMEOUT = int(os.getenv("RSS_FETCH_TIMEOUT", "10"))
DRY_RUN_OUTPUT_PATH = os.getenv("DRY_RUN_OUTPUT_PATH", "data/dry_run_briefing.json")
MAX_RAW_NEWS_CHARS = int(os.getenv("MAX_RAW_NEWS_CHARS", "12000"))
MAX_NEWS_BLOCKS_FOR_AI = int(os.getenv("MAX_NEWS_BLOCKS_FOR_AI", "20"))
EMBED_LAYOUT = os.getenv("EMBED_LAYOUT", "individual").strip().lower()
FAILURE_WEBHOOK_URL = (os.getenv("FAILURE_WEBHOOK_URL") or "").strip()


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


TIER1_ONLY = _env_flag("TIER1_ONLY")


def parse_list_env(value: str | None, *, separator: str = ",") -> list[str]:
    if not value or not value.strip():
        return []
    if separator == "\n" and "\n" in value:
        parts = value.splitlines()
    elif "\n" in value:
        parts = value.splitlines()
    else:
        parts = value.split(separator)
    return [p.strip() for p in parts if p.strip()]


def load_rss_urls(env_value: str | None = None) -> list[str]:
    urls = parse_list_env(env_value if env_value is not None else os.getenv("RSS_URLS"))
    return urls if urls else list(DEFAULT_RSS_URLS)


def load_tier1_sources(env_value: str | None = None) -> list[str]:
    sources = parse_list_env(env_value if env_value is not None else os.getenv("TIER_1_SOURCES"))
    return sources if sources else list(DEFAULT_TIER_1_SOURCES)


RSS_URLS = load_rss_urls()
TIER_1_SOURCES = load_tier1_sources()


def use_test_channel() -> bool:
    return os.getenv("USE_TEST_CHANNEL", "").strip().lower() in ("1", "true", "yes", "on")


def get_channel_id() -> int:
    if use_test_channel():
        test_id = int(os.getenv("TEST_CHANNEL_ID", "0") or "0")
        if test_id > 0:
            return test_id
    return int(os.getenv("CHANNEL_ID", str(CHANNEL_ID)) or "0")


def use_discord_webhook() -> bool:
    url = (os.getenv("DISCORD_WEBHOOK_URL") or DISCORD_WEBHOOK_URL or "").strip()
    if not url:
        return False
    return os.getenv("USE_DISCORD_WEBHOOK", "").strip().lower() in ("1", "true", "yes", "on")


def is_dry_run_env() -> bool:
    return os.getenv("DRY_RUN", "").strip().lower() in ("1", "true", "yes", "on")


class ConfigError(ValueError):
    """필수 환경 변수가 없거나 잘못되었을 때 발생합니다."""


def validate_config(
    *,
    dry_run: bool = False,
    webhook: bool = False,
    discord_token: str | None = None,
    deepseek_api_key: str | None = None,
    channel_id: int | None = None,
    webhook_url: str | None = None,
) -> None:
    api_key = deepseek_api_key if deepseek_api_key is not None else DEEPSEEK_API_KEY
    missing = []
    if not api_key or not str(api_key).strip():
        missing.append("DEEPSEEK_API_KEY")

    if dry_run:
        if missing:
            raise ConfigError(
                "필수 환경 변수가 설정되지 않았습니다: "
                + ", ".join(missing)
                + ". .env 파일을 확인하세요."
            )
        return

    if webhook:
        url = webhook_url if webhook_url is not None else DISCORD_WEBHOOK_URL
        if not url:
            missing.append("DISCORD_WEBHOOK_URL")
    else:
        token = discord_token if discord_token is not None else DISCORD_TOKEN
        ch_id = channel_id if channel_id is not None else get_channel_id()
        if not token or not str(token).strip():
            missing.append("DISCORD_TOKEN")
        if not ch_id or ch_id <= 0:
            missing.append("CHANNEL_ID 또는 TEST_CHANNEL_ID (USE_TEST_CHANNEL=1)")

    if missing:
        raise ConfigError(
            "필수 환경 변수가 설정되지 않았습니다: "
            + ", ".join(missing)
            + ". .env 파일 또는 GitHub Secrets를 확인하세요."
        )
