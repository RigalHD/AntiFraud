from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.domain.misc_types import TransactionChannel, TransactionStatus


@dataclass
class Transaction:
    id: UUID
    user_id: UUID

    amount: Decimal
    currency: str
    status: TransactionStatus
    merchant_id: str
    merchant_category_code: str
    timestamp: datetime
    ip_address: str
    device_id: str
    channel: TransactionChannel
    location: TransactionLocation
    is_fraud: bool
    meta_data: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


@dataclass
class TransactionLocation:
    country: str | None = None
    city: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
