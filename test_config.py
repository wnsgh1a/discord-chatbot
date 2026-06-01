import pytest

from config import ConfigError, validate_config


def test_validate_config_success():
    validate_config(
        discord_token="test-token",
        deepseek_api_key="test-key",
        channel_id=123456789,
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
