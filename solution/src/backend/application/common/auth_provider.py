from abc import abstractmethod
from typing import Protocol

from backend.domain.entity.user import User


class AuthProvider(Protocol):
    @abstractmethod
    async def bind_to_auth(self, user: User) -> None: ...
