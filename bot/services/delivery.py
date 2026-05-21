from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.modules.security.inventory_crypto import InventoryCipher


@dataclass(frozen=True)
class DeliverySnapshot:
    encrypted_text: str
    delivered_at: datetime


def build_delivery_snapshot(*, encrypted_inventory_content: str) -> DeliverySnapshot:
    return DeliverySnapshot(
        encrypted_text=encrypted_inventory_content,
        delivered_at=datetime.now(UTC).replace(tzinfo=None),
    )


def decrypt_delivery_snapshot(*, encrypted_text: str, cipher: InventoryCipher) -> str:
    return cipher.decrypt(encrypted_text)
