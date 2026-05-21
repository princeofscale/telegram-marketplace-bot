from decimal import Decimal

from bot.database.models import SettingModel
from bot.modules.settings.values import (
    SettingKey,
    coerce_setting_value,
    default_setting_value,
)


def test_setting_value_coercion_for_known_keys() -> None:
    assert coerce_setting_value(SettingKey.CAPTCHA_ENABLED, "true") is True
    assert coerce_setting_value(SettingKey.REFERRALS_ENABLED, "false") is False
    assert coerce_setting_value(SettingKey.MIN_DEPOSIT, "100.50") == Decimal("100.50")
    assert coerce_setting_value(SettingKey.GLOBAL_MARKUP, "15") == Decimal("15.00")


def test_setting_defaults_are_typed() -> None:
    assert default_setting_value(SettingKey.CAPTCHA_ENABLED) is True
    assert default_setting_value(SettingKey.REFERRALS_ENABLED) is True
    assert default_setting_value(SettingKey.MIN_DEPOSIT) == Decimal("100.00")
    assert default_setting_value(SettingKey.GLOBAL_MARKUP) == Decimal("15.00")


def test_setting_model_contains_key_value_shape() -> None:
    columns = SettingModel.__table__.columns.keys()

    assert "key" in columns
    assert "value" in columns
    assert "description" in columns
    assert "updated_at" in columns
    assert "created_at" in columns
