from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.database.table.fraud_rule import fraud_rule_table


@dataclass(slots=True, frozen=True)
class SAFraudRuleGateway(FraudRuleGateway):
    session: AsyncSession

    async def get_by_id(self, id: UUID) -> FraudRule | None:
        user = await self.session.get(FraudRule, id)

        return user

    async def get_by_name(self, name: str) -> FraudRule | None:
        stmt = select(FraudRule).where(fraud_rule_table.c.name == name)
        res = await self.session.execute(stmt)

        return res.scalar()

    async def get_many(self) -> Sequence[FraudRule]:
        stmt = select(FraudRule).order_by(
            fraud_rule_table.c.created_at.asc(),
        )

        res = await self.session.execute(stmt)

        return res.scalars().all()
