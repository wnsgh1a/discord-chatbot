from utils import normalize_title, redact_secrets, safe_error_message


def test_normalize_title_aliases():
    assert normalize_title("Man Utd beat Liverpool") == normalize_title(
        "Manchester United beat Liverpool"
    )


def test_redact_secrets_token():
    text = "Error Bearer abcdefghijklmnopqrstuvwxyz1234567890"
    assert "[REDACTED]" in redact_secrets(text)
    assert "abcdefghijklmnopqrstuvwxyz1234567890" not in redact_secrets(text)


def test_safe_error_message():
    assert safe_error_message(ValueError("plain error")) == "plain error"
