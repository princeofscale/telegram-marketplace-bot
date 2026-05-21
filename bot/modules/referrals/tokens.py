from __future__ import annotations
import re

REFERRAL_TOKEN_RE = re.compile(r"^ref_(?P<user_id>[1-9]\d*)$")


class ReferralTokenError(ValueError):
    """Raised when a referral token is structurally valid but forbidden."""


def parse_referral_token(token: str | None, new_user_id: int | None = None) -> int | None:
    """Return inviter Telegram user id from a /start payload.

    Unknown payloads are ignored so marketing campaigns can coexist with referrals.
    """
    if not token:
        return None

    match = REFERRAL_TOKEN_RE.fullmatch(token.strip())
    if not match:
        return None

    invited_by = int(match.group("user_id"))
    if new_user_id is not None and invited_by == new_user_id:
        msg = "self_referral"
        raise ReferralTokenError(msg)

    return invited_by
