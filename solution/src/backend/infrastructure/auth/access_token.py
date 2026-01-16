from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from backend.domain.entity.user import User


@dataclass
class AccessToken:
    user_id: UUID
    token: str
    expires_at: datetime

    user: User
