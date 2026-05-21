from bot.database.models import AuditLogModel
from bot.modules.audit.events import AuditAction, AuditEvent


def test_audit_event_serializes_payload_without_none_values() -> None:
    event = AuditEvent(
        action=AuditAction.USER_REGISTERED,
        actor_id=42,
        target_id="42",
        payload={"referrer": None, "language_code": "en"},
    )

    assert event.payload == {"language_code": "en"}
    assert event.action == AuditAction.USER_REGISTERED


def test_audit_actions_cover_order_lifecycle_events() -> None:
    assert AuditAction.ORDER_CREATED.value == "order_created"
    assert AuditAction.ORDER_COMPLETED.value == "order_completed"
    assert AuditAction.ORDER_CANCELLED.value == "order_cancelled"
    assert AuditAction.ORDER_FAILED.value == "order_failed"
    assert AuditAction.ORDER_REFUNDED.value == "order_refunded"


def test_audit_log_model_contains_required_columns() -> None:
    columns = AuditLogModel.__table__.columns.keys()

    assert "id" in columns
    assert "actor_id" in columns
    assert "action" in columns
    assert "target_id" in columns
    assert "payload" in columns
    assert "created_at" in columns
