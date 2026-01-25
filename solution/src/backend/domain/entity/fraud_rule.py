from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class FraudRule:
    id: UUID

    name: str
    description: str
    dsl_expression: str
    priority: int
    enabled: bool = True

    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


@dataclass
class FraudRuleEvaluationResult:
    id: UUID
    transaction_id: UUID
    rule_id: UUID
    rule_name: str
    priority: int
    matched: bool
    description: str
