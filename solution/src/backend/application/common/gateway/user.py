from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from backend.domain.entity.user import User


class UserGateway(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_many(self, offset: int, limit: int, desc: bool = True) -> Sequence[User]: ...

    @abstractmethod
    async def get_count(self) -> int | None: ...