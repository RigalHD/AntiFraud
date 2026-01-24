from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from backend.domain.entity.fraud_rule import FraudRule, FraudRuleEvaluationResult


class FraudRuleGateway(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> FraudRule | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> FraudRule | None: ...

    @abstractmethod
    async def get_many(self) -> Sequence[FraudRule]: ...


class FraudRuleEvaluationResultGateway(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> FraudRuleEvaluationResult | None: ...
    
    @abstractmethod
    async def get_many(self, transaction_id: UUID | None = None) -> Sequence[FraudRuleEvaluationResult]: ...
