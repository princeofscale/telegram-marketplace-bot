from __future__ import annotations

SETTINGS_CALLBACK = "settings"
LANGUAGE_SETTINGS_CALLBACK = "settings:language"
LANGUAGE_CALLBACK_PREFIX = "language"


def language_callback(language_code: str) -> str:
    return f"{LANGUAGE_CALLBACK_PREFIX}:{language_code}"


def parse_language_callback(callback_data: str) -> str:
    prefix, _, language_code = callback_data.partition(":")
    if prefix != LANGUAGE_CALLBACK_PREFIX or not language_code:
        msg = "invalid_language_callback"
        raise ValueError(msg)
    return language_code
