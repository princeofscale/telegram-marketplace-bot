from __future__ import annotations
from enum import StrEnum


class DepositStatus(StrEnum):
    PENDING = "pending"
    WAITING = "waiting"
    PAID = "paid"
    EXPIRED = "expired"
    FAILED = "failed"
    CANCELLED = "cancelled"
