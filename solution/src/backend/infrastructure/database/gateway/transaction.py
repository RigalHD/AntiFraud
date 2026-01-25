from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.common.gateway.transaction import TransactionGateway
from backend.domain.entity.transaction import Transaction
from backend.domain.misc_types import TransactionStatus
from backend.infrastructure.database.table.transaction import transaction_table


@dataclass(slots=True, frozen=True)
class SATransactionGateway(TransactionGateway):
    session: AsyncSession

    async def get_by_id(self, id: UUID) -> Transaction | None:
        user = await self.session.get(Transaction, id)

        return user

    async def get_many(
        self,
        from_: datetime,
        to: datetime,
        offset: int = 0,
        size: int = 20,
        user_id: UUID | None = None,
        status: TransactionStatus | None = None,
        is_fraud: bool | None = None,
    ) -> Sequence[Transaction]:
        stmt = (
            select(Transaction)
            .order_by(transaction_table.c.timestamp.asc())
            .where(transaction_table.c.created_at >= from_)
            .where(transaction_table.c.created_at <= to)
        )

        if user_id is not None:
            stmt = stmt.where(transaction_table.c.user_id == user_id)
        if status is not None:
            stmt = stmt.where(transaction_table.c.status == status)
        if is_fraud is not None:
            stmt = stmt.where(transaction_table.c.is_fraud == is_fraud)

        stmt = stmt.offset(offset).limit(size)

        res = await self.session.execute(stmt)

        return res.scalars().all()

    async def get_count(
        self,
        from_: datetime,
        to: datetime,
        user_id: UUID | None = None,
        status: TransactionStatus | None = None,
        is_fraud: bool | None = None,
    ) -> int | None:
        stmt = (
            select(func.count())
            .select_from(transaction_table)
            .where(transaction_table.c.created_at >= from_)
            .where(transaction_table.c.created_at <= to)
        )

        if user_id is not None:
            stmt = stmt.where(transaction_table.c.user_id == user_id)
        if status is not None:
            stmt = stmt.where(transaction_table.c.status == status)
        if is_fraud is not None:
            stmt = stmt.where(transaction_table.c.is_fraud == is_fraud)

        res = await self.session.execute(stmt)

        return res.scalar()
