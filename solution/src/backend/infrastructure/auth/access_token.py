from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from backend.domain.entity.user import User
from backend.domain.misc_types import Role


@dataclass
class AccessToken:
    user_id: UUID
    role: Role
    token: str

    created_at: datetime
    expires_in: int

    user: User | None = None
