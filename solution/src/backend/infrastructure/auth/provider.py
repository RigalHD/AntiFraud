from dataclasses import dataclass
from uuid import uuid4
from pydantic import BaseModel

from backend.application.common.auth_provider import AuthProvider
from backend.domain.entity.user import User
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.user import WebUser
from backend.infrastructure.common.gateway import WebUserGateway


class WebUserForm(BaseModel):
    ...


@dataclass(slots=True, frozen=True)
class WebAuthProvider(AuthProvider):
    hasher: Hasher
    gateway: WebUserGateway
    form: WebUserForm

    def bind_to_auth(self, user: User) -> None:
        raise NotImplementedError