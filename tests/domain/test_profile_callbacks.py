import pytest

from bot.modules.profile.callbacks import language_callback, parse_language_callback


def test_language_callbacks_roundtrip_language_code() -> None:
    callback_data = language_callback("ru")

    assert parse_language_callback(callback_data) == "ru"


def test_language_callbacks_reject_invalid_prefix() -> None:
    with pytest.raises(ValueError, match="invalid_language_callback"):
        parse_language_callback("locale:ru")
