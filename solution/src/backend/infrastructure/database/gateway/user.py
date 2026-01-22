from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.common.gateway.user import UserGateway
from backend.domain.entity.user import User
from backend.infrastructure.database.table.user import user_table


@dataclass(slots=True, frozen=True)
class SAUserGateway(UserGateway):
    session: AsyncSession

    async def get_by_id(self, id: UUID) -> User | None:
        user = await self.session.get(User, id)

        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(user_table.c.email == email)
        res = await self.session.execute(stmt)

        return res.scalar()

    async def get_many(self, offset: int, size: int) -> Sequence[User]:
        stmt = select(User).offset(offset).limit(size)
        stmt = stmt.order_by(user_table.c.created_at.asc())

        res = await self.session.execute(stmt)

        return res.scalars().all()

    async def get_count(self) -> int | None:
        stmt = select(func.count()).select_from(user_table)
        res = await self.session.execute(stmt)

        return res.scalar()
