from dataclasses import dataclass
from uuid import UUID

from backend.domain.entity.transaction import Transaction


@dataclass
class FraudRuleEvaluationResultDTO:
    rule_id: UUID
    rule_name: str
    priority: int
    matched: bool
    description: str


@dataclass(slots=True, frozen=True)
class TransactionDecision:
    transaction: Transaction
    rule_results: list[FraudRuleEvaluationResultDTO]


@dataclass(slots=True, frozen=True)
class TransactionsList:
    items: list[Transaction]
    total: int
    page: int
    size: int
