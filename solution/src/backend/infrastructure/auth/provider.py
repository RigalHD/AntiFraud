from dataclasses import dataclass
from uuid import uuid4
from backend.domain.misc_types import Gender, MaritalStatus
from pydantic import BaseModel, Field

from backend.application.common.auth_provider import AuthProvider
from backend.domain.entity.user import User
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.user import WebUser
from backend.infrastructure.common.gateway import WebUserGateway


class WebUserAuthForm(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72)
    fullName: str = Field(min_length=2, max_length=200)
    age: int | None = Field(default=None, ge=18, le=120)
    region: str | None = Field(default=None, max_length=32)
    gender: Gender | None = Field(default=None)
    maritalStatus: MaritalStatus | None = Field(default=None)
    


@dataclass(slots=True, frozen=True)
class WebAuthProvider(AuthProvider):
    hasher: Hasher
    gateway: WebUserGateway
    form: WebUserAuthForm

    def bind_to_auth(self, user: User) -> None:
        raise NotImplementedError