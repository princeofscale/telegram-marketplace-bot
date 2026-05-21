from __future__ import annotations
from dataclasses import dataclass

from bot.cache.redis import redis_client, set_redis_value

REGISTRATION_TTL_SECONDS = 600
NO_REFERRER_VALUE = "-"


@dataclass(frozen=True)
class PendingRegistration:
    referrer: str | None


def pending_registration_key(user_id: int) -> str:
    return f"registration:pending:{user_id}"


async def create_pending_registration(user_id: int, referrer: str | None) -> None:
    await set_redis_value(
        key=pending_registration_key(user_id),
        value=referrer or NO_REFERRER_VALUE,
        ttl=REGISTRATION_TTL_SECONDS,
    )


async def pop_pending_registration(user_id: int) -> PendingRegistration | None:
    key = pending_registration_key(user_id)
    value = await redis_client.get(key)
    await redis_client.delete(key)

    if value is None:
        return None

    referrer = value.decode("utf-8")
    return PendingRegistration(referrer=None if referrer == NO_REFERRER_VALUE else referrer)
