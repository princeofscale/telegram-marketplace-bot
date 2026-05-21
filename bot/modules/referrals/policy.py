from __future__ import annotations
from dataclasses import dataclass

from bot.modules.referrals.tokens import ReferralTokenError, parse_referral_token


@dataclass(frozen=True)
class ReferralApplyDecision:
    invited_by: int | None = None
    should_increment_inviter: bool = False


def decide_referral_application(
    *,
    new_user_id: int,
    token: str | None,
    existing_invited_by: int | None,
    inviter_exists: bool,
) -> ReferralApplyDecision:
    if existing_invited_by is not None:
        return ReferralApplyDecision()

    try:
        invited_by = parse_referral_token(token, new_user_id=new_user_id)
    except ReferralTokenError:
        return ReferralApplyDecision()

    if invited_by is None or not inviter_exists:
        return ReferralApplyDecision()

    return ReferralApplyDecision(invited_by=invited_by, should_increment_inviter=True)
