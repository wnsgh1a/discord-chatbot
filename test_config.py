import pytest

from config import (
    ConfigError,
    get_channel_id,
    load_rss_urls,
    load_tier1_sources,
    parse_list_env,
    use_discord_webhook,
    use_test_channel,
    validate_config,
)


def test_validate_config_success():
    validate_config(
        discord_token="test-token",
        deepseek_api_key="test-key",
        channel_id=123456789,
    )


def test_validate_config_dry_run_only_needs_api_key():
    validate_config(dry_run=True, deepseek_api_key="key")


def test_validate_config_dry_run_missing_api_key():
    with pytest.raises(ConfigError, match="DEEPSEEK_API_KEY"):
        validate_config(dry_run=True, deepseek_api_key="")


def test_validate_config_webhook_mode():
    validate_config(
        webhook=True,
        deepseek_api_key="key",
        webhook_url="https://discord.com/api/webhooks/1/token",
    )


def test_validate_config_missing_discord_token():
    with pytest.raises(ConfigError, match="DISCORD_TOKEN"):
        validate_config(discord_token="", deepseek_api_key="key", channel_id=1)


def test_validate_config_missing_deepseek_key():
    with pytest.raises(ConfigError, match="DEEPSEEK_API_KEY"):
        validate_config(discord_token="token", deepseek_api_key=None, channel_id=1)


def test_validate_config_invalid_channel_id():
    with pytest.raises(ConfigError, match="CHANNEL_ID"):
        validate_config(discord_token="token", deepseek_api_key="key", channel_id=0)


def test_parse_list_env_comma_separated():
    assert parse_list_env("a, b ,c") == ["a", "b", "c"]


def test_parse_list_env_newlines():
    assert parse_list_env("a\nb\nc") == ["a", "b", "c"]


def test_load_rss_urls_default():
    assert len(load_rss_urls("")) >= 3


def test_load_rss_urls_custom():
    custom = "https://example.com/feed.xml,https://example.com/feed2.xml"
    urls = load_rss_urls(custom)
    assert urls == ["https://example.com/feed.xml", "https://example.com/feed2.xml"]


def test_load_tier1_sources_custom():
    sources = load_tier1_sources("Reporter A, Reporter B")
    assert sources == ["Reporter A", "Reporter B"]


def test_get_channel_id_uses_test_channel(monkeypatch):
    monkeypatch.setenv("USE_TEST_CHANNEL", "1")
    monkeypatch.setenv("TEST_CHANNEL_ID", "999")
    monkeypatch.setenv("CHANNEL_ID", "111")
    assert get_channel_id() == 999


def test_use_discord_webhook_flag(monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/x/y")
    monkeypatch.setenv("USE_DISCORD_WEBHOOK", "true")
    assert use_discord_webhook() is True


def test_use_test_channel_flag(monkeypatch):
    monkeypatch.setenv("USE_TEST_CHANNEL", "yes")
    assert use_test_channel() is True
