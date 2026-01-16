from __future__ import annotations

from abc import abstractmethod
from types import TracebackType
from typing import Any, Protocol


class IStorageClient(Protocol):
    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int | None = None) -> bool: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> IStorageClient: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
