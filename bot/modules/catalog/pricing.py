from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MarkupPolicy:
    global_markup: Decimal
    category_markup: Decimal | None = None
    product_markup: Decimal | None = None

    @property
    def effective_markup(self) -> Decimal:
        return self.product_markup or self.category_markup or self.global_markup


def calculate_display_price(base_price: Decimal, policy: MarkupPolicy) -> Decimal:
    multiplier = Decimal("1.00") + (policy.effective_markup / Decimal(100))
    return (base_price * multiplier).quantize(Decimal("0.01"))
