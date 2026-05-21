from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from bot.database.models import CatalogProductModel, DepositModel, InventoryItemModel, OrderModel, UserModel
from bot.modules.payments.deposits import DepositStatus

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class AdminStats:
    users_count: int
    admins_count: int
    deposits_count: int
    paid_deposits_count: int
    paid_deposits_amount: Decimal
    orders_count: int
    catalog_products_count: int
    inventory_items_count: int


async def get_admin_stats(session: AsyncSession) -> AdminStats:
    return AdminStats(
        users_count=await count_rows(session, UserModel),
        admins_count=await count_rows(session, UserModel, UserModel.is_admin.is_(True)),
        deposits_count=await count_rows(session, DepositModel),
        paid_deposits_count=await count_rows(session, DepositModel, DepositModel.status == DepositStatus.PAID.value),
        paid_deposits_amount=await sum_decimal(
            session,
            DepositModel.amount,
            DepositModel.status == DepositStatus.PAID.value,
        ),
        orders_count=await count_rows(session, OrderModel),
        catalog_products_count=await count_rows(session, CatalogProductModel),
        inventory_items_count=await count_rows(session, InventoryItemModel),
    )


async def count_rows(session: AsyncSession, model: type, *conditions: object) -> int:
    query = select(func.count()).select_from(model)
    if conditions:
        query = query.where(*conditions)
    result = await session.execute(query)
    return int(result.scalar_one() or 0)


async def sum_decimal(session: AsyncSession, column: object, *conditions: object) -> Decimal:
    query = select(func.coalesce(func.sum(column), Decimal("0.00")))
    if conditions:
        query = query.where(*conditions)
    result = await session.execute(query)
    return Decimal(result.scalar_one() or Decimal("0.00"))
