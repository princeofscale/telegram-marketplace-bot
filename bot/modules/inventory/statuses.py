from __future__ import annotations
from enum import StrEnum


class InventoryStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    CANCELLED = "cancelled"
    HIDDEN = "hidden"
