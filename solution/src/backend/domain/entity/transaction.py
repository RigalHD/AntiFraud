from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.domain.misc_types import TransactionChannel, TransactionStatus

type MetaDataJSON = dict[str, Any]


@dataclass
class Transaction:
    id: UUID
    user_id: UUID

    amount: Decimal
    currency: str
    status: TransactionStatus
    merchant_id: str | None
    merchant_category_code: str | None
    timestamp: datetime
    ip_address: str | None
    device_id: str | None
    channel: TransactionChannel | None
    location: TransactionLocation | None
    is_fraud: bool
    metadata: MetaDataJSON | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


@dataclass
class TransactionLocation:
    country: str | None = None
    city: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
