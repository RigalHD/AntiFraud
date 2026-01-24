from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from backend.domain.entity.transaction import Transaction
from backend.domain.misc_types import TransactionStatus


class TransactionGateway(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Transaction | None: ...

    @abstractmethod
    async def get_many(
        self,
        from_: datetime,
        to: datetime,
        offset: int = 0,
        size: int = 20,
        user_id: UUID | None = None,
        status: TransactionStatus | None = None,
        is_fraud: bool | None = None,
    ) -> Sequence[Transaction]: ...
