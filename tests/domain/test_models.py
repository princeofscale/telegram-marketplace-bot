from bot.database.models import UserBalanceTransactionModel, UserModel


def test_user_model_contains_marketplace_accounting_fields() -> None:
    columns = UserModel.__table__.columns.keys()

    assert "role" in columns
    assert "invited_by" in columns
    assert "referrals_count" in columns
    assert "referral_earnings" in columns
    assert "balance" in columns
    assert "total_deposited" in columns
    assert "total_spent" in columns
    assert "is_blocked" in columns
    assert "banned_reason" in columns
    assert "registered_at" in columns
    assert "last_activity_at" in columns
    assert "updated_at" in columns


def test_balance_transaction_model_is_append_only_ledger_shape() -> None:
    columns = UserBalanceTransactionModel.__table__.columns.keys()

    assert "id" in columns
    assert "user_id" in columns
    assert "amount" in columns
    assert "type" in columns
    assert "balance_before" in columns
    assert "balance_after" in columns
    assert "comment" in columns
    assert "created_at" in columns
