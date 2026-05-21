import pytest

from bot.modules.referrals.policy import ReferralApplyDecision, decide_referral_application
from bot.modules.referrals.tokens import ReferralTokenError, parse_referral_token

INVITER_ID = 123456789


def test_parse_referral_token_accepts_ref_user_id() -> None:
    assert parse_referral_token(f"ref_{INVITER_ID}") == INVITER_ID


def test_parse_referral_token_rejects_self_referral() -> None:
    with pytest.raises(ReferralTokenError, match="self_referral"):
        parse_referral_token("ref_42", new_user_id=42)


def test_parse_referral_token_ignores_unknown_start_payloads() -> None:
    assert parse_referral_token("campaign_spring") is None
    assert parse_referral_token(None) is None


def test_referral_application_accepts_first_valid_inviter() -> None:
    start_payload = "ref_200"
    decision = decide_referral_application(
        new_user_id=100,
        token=start_payload,
        existing_invited_by=None,
        inviter_exists=True,
    )

    assert decision == ReferralApplyDecision(invited_by=200, should_increment_inviter=True)


def test_referral_application_rejects_missing_inviter_and_existing_assignment() -> None:
    start_payload = "ref_200"
    missing = decide_referral_application(
        new_user_id=100,
        token=start_payload,
        existing_invited_by=None,
        inviter_exists=False,
    )
    already_assigned = decide_referral_application(
        new_user_id=100,
        token=start_payload,
        existing_invited_by=300,
        inviter_exists=True,
    )

    assert missing == ReferralApplyDecision()
    assert already_assigned == ReferralApplyDecision()
