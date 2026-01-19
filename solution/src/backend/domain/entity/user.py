from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from backend.domain.misc_types import Gender, Role


@dataclass
class User:
    user_id: UUID
    
    email: str
    password: str
    full_name: str
    
    age: int | None = None
    region: str | None = None
    gender: Gender | None = None
    marital_status: str | None = None
    
    role: Role = Role.USER
    is_active: bool = True
    
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
