import re

SENSITIVE_ENV_KEYS = (
    "DISCORD_TOKEN",
    "DEEPSEEK_API_KEY",
    "DISCORD_WEBHOOK_URL",
    "FAILURE_WEBHOOK_URL",
)

_TOKEN_LIKE = re.compile(
    r"(Bearer\s+)?[A-Za-z0-9_\-\.]{20,}|sk-[A-Za-z0-9]{10,}",
    re.IGNORECASE,
)

_TITLE_ALIASES = (
    (r"\bman utd\b", "manchester united"),
    (r"\bmanu\b", "manchester united"),
    (r"\bmufc\b", "manchester united"),
    (r"\bred devils\b", "manchester united"),
)


def env_flag(name: str) -> bool:
    import os

    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def normalize_title(title: str) -> str:
    text = title.lower()
    for pattern, replacement in _TITLE_ALIASES:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def redact_secrets(text: str) -> str:
    if not text:
        return text
    redacted = _TOKEN_LIKE.sub("[REDACTED]", text)
    for key in SENSITIVE_ENV_KEYS:
        import os

        value = os.getenv(key, "")
        if value and len(value) > 8 and value in redacted:
            redacted = redacted.replace(value, "[REDACTED]")
    return redacted


def safe_error_message(exc: BaseException) -> str:
    return redact_secrets(str(exc))
