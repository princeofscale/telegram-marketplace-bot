from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AuditAction(StrEnum):
    USER_REGISTERED = "user_registered"
    REFERRAL_APPLIED = "referral_applied"
    ADMIN_ACTION = "admin_action"
    BALANCE_CHANGED = "balance_changed"
    DEPOSIT_CREATED = "deposit_created"
    DEPOSIT_VERIFIED = "deposit_verified"
    ORDER_CREATED = "order_created"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_FAILED = "order_failed"
    ORDER_REFUNDED = "order_refunded"
    SETTING_CHANGED = "setting_changed"
    SUSPICIOUS_ACTION = "suspicious_action"


@dataclass(frozen=True)
class AuditEvent:
    action: AuditAction
    actor_id: int | None = None
    target_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        clean_payload = {key: value for key, value in self.payload.items() if value is not None}
        object.__setattr__(self, "payload", clean_payload)
