from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass
class User:
    user_id: UUID
    
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
