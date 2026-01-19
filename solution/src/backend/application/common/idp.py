from abc import abstractmethod
from typing import Protocol

from backend.domain.entity.user import User


class UserIdProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User: ...

    @abstractmethod
    async def get_user_or_none(self) -> User | None: ...
