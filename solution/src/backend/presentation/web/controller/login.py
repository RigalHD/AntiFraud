from dataclasses import dataclass

from backend.application.common.gateway.user import UserGateway
from backend.application.exception.user import InactiveUserError
from backend.domain.entity.user import User
from backend.infrastructure.auth.exception import UnauthorizedError
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.idp.token_processor import EXPIRATION_TIME, AccessTokenProcessor
from backend.infrastructure.auth.login import WebLoginForm


@dataclass(slots=True, frozen=True)
class LoginResponse:
    access_token: str
    expires_in: int
    user: User


@dataclass(slots=True, frozen=True)
class WebLogin:
    gateway: UserGateway
    hasher: Hasher
    processor: AccessTokenProcessor

    async def execute(self, form: WebLoginForm) -> LoginResponse:
        user = await self.gateway.get_by_email(form.email)

        if (user is None) or (self.hasher.verify(form.password, user.password) is False):
            raise UnauthorizedError

        if user.is_active is False:
            raise InactiveUserError

        return LoginResponse(
            access_token=self.processor.encode(user_id=user.id, role=user.role),
            expires_in=EXPIRATION_TIME,
            user=user,
        )
