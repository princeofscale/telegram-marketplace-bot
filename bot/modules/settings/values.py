from __future__ import annotations
from decimal import Decimal
from enum import StrEnum
from typing import Any


class SettingKey(StrEnum):
    GLOBAL_MARKUP = "global_markup"
    CAPTCHA_ENABLED = "captcha_enabled"
    REFERRALS_ENABLED = "referrals_enabled"
    MIN_DEPOSIT = "min_deposit"


SETTING_DEFAULTS: dict[SettingKey, bool | Decimal] = {
    SettingKey.GLOBAL_MARKUP: Decimal("15.00"),
    SettingKey.CAPTCHA_ENABLED: True,
    SettingKey.REFERRALS_ENABLED: True,
    SettingKey.MIN_DEPOSIT: Decimal("100.00"),
}


def default_setting_value(key: SettingKey) -> bool | Decimal:
    return SETTING_DEFAULTS[key]


def coerce_setting_value(key: SettingKey, value: Any) -> bool | Decimal:
    if key in {SettingKey.CAPTCHA_ENABLED, SettingKey.REFERRALS_ENABLED}:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    return Decimal(str(value)).quantize(Decimal("0.01"))


def serialize_setting_value(value: bool | Decimal) -> bool | str:
    if isinstance(value, Decimal):
        return str(value.quantize(Decimal("0.01")))
    return value
