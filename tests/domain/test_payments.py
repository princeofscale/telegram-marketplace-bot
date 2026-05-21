from decimal import Decimal
from uuid import uuid4

from bot.database.models import DepositModel
from bot.modules.payments.callbacks import (
    CHECK_DEPOSIT_CALLBACK_PREFIX,
    DEPOSIT_CALLBACK_PREFIX,
    check_deposit_callback,
    deposit_callback,
    deposit_details_callback,
    deposit_history_page_callback,
    deposit_method_callback,
    parse_check_deposit_callback,
    parse_deposit_callback,
    parse_deposit_details_callback,
    parse_deposit_history_page_callback,
    parse_deposit_method_callback,
)
from bot.modules.payments.deposits import DepositStatus
from bot.modules.payments.lolz import (
    LOLZ_BALANCE_PAYMENT_METHOD,
    build_lolz_transfer_comment,
    build_lolz_transfer_link,
)
from bot.modules.payments.platega import (
    PLATEGA_PAYMENT_METHODS,
    CommissionPayer,
    PlategaPaymentMethod,
    build_platega_return_url,
    calculate_deposit_pricing,
    map_platega_status,
)
from bot.modules.payments.provider import PaymentVerification
from bot.services.lolz_payments import LolzBalanceClient
from bot.services.payments import build_provider_payment_id, build_verified_deposit_update, create_manual_deposit

SBP_QR_PROVIDER_METHOD_ID = 2
CRYPTO_PROVIDER_METHOD_ID = 13
HISTORY_PAGE = 2


def test_payment_verification_requires_matching_paid_provider_response() -> None:
    verification = PaymentVerification(
        provider_payment_id="pay_1",
        status=DepositStatus.PAID,
        amount=Decimal("100.00"),
    )

    update = build_verified_deposit_update(
        expected_amount=Decimal("100.00"),
        expected_provider_payment_id="pay_1",
        verification=verification,
    )

    assert update.status == DepositStatus.PAID
    assert update.paid_amount == Decimal("100.00")


def test_payment_verification_rejects_amount_or_payment_id_mismatch() -> None:
    wrong_amount = PaymentVerification(
        provider_payment_id="pay_1",
        status=DepositStatus.PAID,
        amount=Decimal("99.99"),
    )
    wrong_id = PaymentVerification(
        provider_payment_id="pay_2",
        status=DepositStatus.PAID,
        amount=Decimal("100.00"),
    )

    assert (
        build_verified_deposit_update(
            expected_amount=Decimal("100.00"),
            expected_provider_payment_id="pay_1",
            verification=wrong_amount,
        ).status
        == DepositStatus.FAILED
    )
    assert (
        build_verified_deposit_update(
            expected_amount=Decimal("100.00"),
            expected_provider_payment_id="pay_1",
            verification=wrong_id,
        ).status
        == DepositStatus.FAILED
    )


def test_deposit_model_contains_provider_verification_shape() -> None:
    columns = DepositModel.__table__.columns.keys()

    assert "id" in columns
    assert "user_id" in columns
    assert "amount" in columns
    assert "requested_amount" in columns
    assert "commission_amount" in columns
    assert "payment_method" in columns
    assert "provider_payment_id" in columns
    assert "payment_url" in columns
    assert "status" in columns
    assert "created_at" in columns
    assert "paid_at" in columns


def test_manual_deposit_entrypoints_exist() -> None:
    provider_payment_id = build_provider_payment_id(user_id=42)

    assert provider_payment_id.startswith("manual:42:")
    assert callable(create_manual_deposit)


def test_deposit_callbacks_roundtrip_amounts() -> None:
    callback_data = deposit_callback(Decimal(25))

    assert callback_data.startswith(f"{DEPOSIT_CALLBACK_PREFIX}:")
    assert parse_deposit_callback(callback_data) == Decimal("25.00")


def test_deposit_method_callbacks_roundtrip_amount_and_method() -> None:
    callback_data = deposit_method_callback(Decimal(25), PlategaPaymentMethod.SBP_QR.value)

    amount, payment_method = parse_deposit_method_callback(callback_data)

    assert amount == Decimal("25.00")
    assert payment_method == PlategaPaymentMethod.SBP_QR.value


def test_lolz_balance_transfer_link_contains_receiver_amount_and_unique_comment() -> None:
    comment = build_lolz_transfer_comment(user_id=42, deposit_id="abc")

    payment_url = build_lolz_transfer_link(
        username="princeofscale",
        amount=Decimal("100.00"),
        comment=comment,
    )
    callback_data = deposit_method_callback(Decimal("100.00"), LOLZ_BALANCE_PAYMENT_METHOD)

    assert comment == "lolz:42:abc"
    assert payment_url.startswith("https://lzt.market/balance/transfer?")
    assert "username=princeofscale" in payment_url
    assert "amount=100.00" in payment_url
    assert "comment=lolz%3A42%3Aabc" in payment_url
    assert parse_deposit_method_callback(callback_data) == (Decimal("100.00"), LOLZ_BALANCE_PAYMENT_METHOD)


async def test_lolz_balance_client_verifies_income_by_comment_and_amount() -> None:
    client = LolzBalanceClient(
        access_token="header.payload.signature",  # noqa: S106
        market_factory=lambda **_: FakeLolzMarket(),
    )

    verification = await client.verify_payment("lolz:42:abc")

    assert verification.provider_payment_id == "lolz:42:abc"
    assert verification.status == DepositStatus.PAID
    assert verification.amount == Decimal("100.00")


def test_check_deposit_callbacks_roundtrip_provider_payment_ids() -> None:
    callback_data = check_deposit_callback("transaction-id")

    assert callback_data.startswith(f"{CHECK_DEPOSIT_CALLBACK_PREFIX}:")
    assert parse_check_deposit_callback(callback_data) == "transaction-id"


def test_deposit_history_page_callbacks_roundtrip_pages() -> None:
    callback_data = deposit_history_page_callback(HISTORY_PAGE)

    assert parse_deposit_history_page_callback(callback_data) == HISTORY_PAGE


def test_deposit_details_callbacks_roundtrip_ids() -> None:
    deposit_id = uuid4()
    callback_data = deposit_details_callback(deposit_id)

    assert parse_deposit_details_callback(callback_data) == deposit_id


def test_platega_status_and_return_url_mapping() -> None:
    deposit_id = uuid4()

    assert map_platega_status("CONFIRMED") == DepositStatus.PAID
    assert map_platega_status("CANCELED") == DepositStatus.CANCELLED
    assert map_platega_status("PENDING") == DepositStatus.PENDING
    assert build_platega_return_url(bot_public_url="https://t.me/VoxMarketBot", deposit_id=deposit_id).startswith(
        "https://t.me/VoxMarketBot?start=deposit_",
    )


def test_client_paid_commission_increases_payment_amount_without_increasing_balance_credit() -> None:
    pricing = calculate_deposit_pricing(
        balance_amount=Decimal("100.00"),
        policy=PLATEGA_PAYMENT_METHODS[PlategaPaymentMethod.SBP_QR],
    )

    assert pricing.balance_amount == Decimal("100.00")
    assert pricing.payment_amount == Decimal("110.00")
    assert pricing.commission_amount == Decimal("10.00")
    assert pricing.commission_payer == CommissionPayer.CLIENT
    assert pricing.provider_method_id == SBP_QR_PROVIDER_METHOD_ID


def test_crypto_commission_uses_confirmed_platega_method_id() -> None:
    pricing = calculate_deposit_pricing(
        balance_amount=Decimal("100.00"),
        policy=PLATEGA_PAYMENT_METHODS[PlategaPaymentMethod.CRYPTO],
    )

    assert pricing.payment_amount == Decimal("104.00")
    assert pricing.provider_method_id == CRYPTO_PROVIDER_METHOD_ID


class FakeLolzResponse:
    status_code = 200
    text = "{}"

    def json(self) -> dict[str, object]:
        return {
            "payments": [
                {
                    "payment_id": 123,
                    "type": "income",
                    "amount": 100,
                    "currency": "rub",
                    "comment": "lolz:42:abc",
                    "hold": False,
                },
            ],
        }


class FakeLolzPayments:
    def __init__(self) -> None:
        self.history_calls: list[dict[str, object]] = []

    async def history(self, **kwargs: object) -> FakeLolzResponse:
        self.history_calls.append(kwargs)
        return FakeLolzResponse()


class FakeLolzMarket:
    def __init__(self) -> None:
        self.payments = FakeLolzPayments()
        self.settings = FakeLolzSettings()


class FakeLolzSettings:
    base_url = ""
