from __future__ import annotations
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update

from bot.cache.redis import build_key, cached, clear_cache
from bot.core.config import settings
from bot.database.models import UserModel
from bot.database.models.user import UserRole
from bot.modules.admins.policy import is_default_admin_user
from bot.modules.audit.events import AuditAction, AuditEvent
from bot.modules.referrals.policy import decide_referral_application
from bot.modules.referrals.tokens import ReferralTokenError, parse_referral_token
from bot.services.audit import add_audit_log

if TYPE_CHECKING:
    from aiogram.types import User
    from sqlalchemy.ext.asyncio import AsyncSession


async def add_user(
    session: AsyncSession,
    user: User,
    referrer: str | None,
) -> int | None:
    """Add a new user to the database."""
    user_id: int = user.id
    first_name: str = user.first_name
    last_name: str | None = user.last_name
    username: str | None = user.username
    language_code: str | None = user.language_code
    is_premium: bool = user.is_premium or False
    inviter_id = parse_inviter_id(referrer, user_id)
    is_default_admin = is_default_admin_user(user_id, settings.default_admin_user_ids)

    referral_decision = decide_referral_application(
        new_user_id=user_id,
        token=referrer,
        existing_invited_by=None,
        inviter_exists=await user_exists(session, user_id=inviter_id) if inviter_id is not None else False,
    )

    new_user = UserModel(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        language_code=language_code,
        is_premium=is_premium,
        referrer=referrer,
        invited_by=referral_decision.invited_by,
        is_admin=is_default_admin,
        role=UserRole.OWNER.value if is_default_admin else UserRole.USER.value,
    )

    session.add(new_user)
    add_audit_log(
        session,
        AuditEvent(
            action=AuditAction.USER_REGISTERED,
            actor_id=user_id,
            target_id=str(user_id),
            payload={
                "username": username,
                "language_code": language_code,
                "referrer": referrer,
                "invited_by": referral_decision.invited_by,
            },
        ),
    )
    if referral_decision.should_increment_inviter and referral_decision.invited_by is not None:
        stmt = (
            update(UserModel)
            .where(UserModel.id == referral_decision.invited_by)
            .values(referrals_count=UserModel.referrals_count + 1)
        )
        await session.execute(stmt)
        add_audit_log(
            session,
            AuditEvent(
                action=AuditAction.REFERRAL_APPLIED,
                actor_id=user_id,
                target_id=str(referral_decision.invited_by),
                payload={"invited_user_id": user_id},
            ),
        )

    await session.commit()
    await clear_cache(user_exists, user_id)
    await clear_cache(get_all_users)
    await clear_cache(get_user_count)
    return referral_decision.invited_by


def parse_inviter_id(referrer: str | None, user_id: int) -> int | None:
    try:
        return parse_referral_token(referrer, new_user_id=user_id)
    except ReferralTokenError:
        return None


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user is in the database."""
    query = select(UserModel.id).filter_by(id=user_id).limit(1)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return bool(user)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_first_name(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.first_name).filter_by(id=user_id)

    result = await session.execute(query)

    first_name = result.scalar_one_or_none()
    return first_name or ""


async def get_user(session: AsyncSession, user_id: int) -> UserModel | None:
    query = select(UserModel).filter_by(id=user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_language_code(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.language_code).filter_by(id=user_id)

    result = await session.execute(query)

    language_code = result.scalar_one_or_none()
    return language_code or ""


async def set_language_code(
    session: AsyncSession,
    user_id: int,
    language_code: str,
) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(language_code=language_code)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(get_language_code, user_id)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def is_admin(session: AsyncSession, user_id: int) -> bool:
    if is_default_admin_user(user_id, settings.default_admin_user_ids):
        return True

    query = select(UserModel.is_admin).filter_by(id=user_id)

    result = await session.execute(query)

    is_admin = result.scalar_one_or_none()
    return bool(is_admin)


async def set_is_admin(session: AsyncSession, user_id: int, is_admin: bool) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(is_admin=is_admin)

    await session.execute(stmt)
    await session.commit()
    await clear_cache(is_admin, user_id)


async def sync_user_profile(session: AsyncSession, user: User) -> bool:
    values = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code,
        "is_premium": user.is_premium or False,
        "last_activity_at": datetime.now(UTC).replace(tzinfo=None),
    }
    if is_default_admin_user(user.id, settings.default_admin_user_ids):
        values["is_admin"] = True
        values["role"] = UserRole.OWNER.value

    stmt = update(UserModel).where(UserModel.id == user.id).values(**values)

    result = await session.execute(stmt)
    await session.commit()

    await clear_cache(get_first_name, user.id)
    await clear_cache(get_language_code, user.id)
    await clear_cache(is_admin, user.id)
    await clear_cache(get_all_users)
    return bool(result.rowcount)


@cached(key_builder=lambda session: build_key())
async def get_all_users(session: AsyncSession) -> list[UserModel]:
    query = select(UserModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


@cached(key_builder=lambda session: build_key())
async def get_user_count(session: AsyncSession) -> int:
    query = select(func.count()).select_from(UserModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)
