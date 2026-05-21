from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import select

from bot.database.models import SettingModel
from bot.modules.audit.events import AuditAction, AuditEvent
from bot.modules.settings.values import (
    SettingKey,
    coerce_setting_value,
    default_setting_value,
    serialize_setting_value,
)
from bot.services.audit import add_audit_log

if TYPE_CHECKING:
    from decimal import Decimal

    from sqlalchemy.ext.asyncio import AsyncSession


async def get_setting(session: AsyncSession, key: SettingKey) -> bool | Decimal:
    result = await session.execute(select(SettingModel).where(SettingModel.key == key.value))
    setting = result.scalar_one_or_none()
    if setting is None:
        return default_setting_value(key)
    return coerce_setting_value(key, setting.value)


async def set_setting(
    session: AsyncSession,
    key: SettingKey,
    value: bool | Decimal | str,
    description: str | None = None,
    actor_id: int | None = None,
) -> SettingModel:
    coerced_value = coerce_setting_value(key, value)
    serialized_value = serialize_setting_value(coerced_value)
    result = await session.execute(select(SettingModel).where(SettingModel.key == key.value))
    setting = result.scalar_one_or_none()

    if setting is None:
        setting = SettingModel(key=key.value, value=serialized_value, description=description)
        session.add(setting)
    else:
        setting.value = serialized_value
        if description is not None:
            setting.description = description

    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.SETTING_CHANGED,
            actor_id=actor_id,
            target_id=key.value,
            payload={"value": serialized_value, "description": description},
        ),
    )
    await session.commit()
    return setting
