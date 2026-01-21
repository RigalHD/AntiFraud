from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import jwt

from backend.domain.misc_types import Role

ALG = "HS256"
EXPIRATION_TIME = 3600


@dataclass(slots=True, frozen=True)
class AccessTokenProcessor:
    secret_key: str

    def encode(self, user_id: UUID, role: Role) -> str:
        return jwt.encode(
            {
                "sub": str(user_id),
                "role": role.value,
                "iat": int(datetime.now(tz=UTC).timestamp()),
                "exp": EXPIRATION_TIME,
            },
            self.secret_key,
            ALG,
        )

    def decode(self, content: str) -> Any:
        return jwt.decode(
            content,
            self.secret_key,
            algorithms=[ALG],
            options={
                "verify_exp": False,
            },
        )
