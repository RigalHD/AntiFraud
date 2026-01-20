from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi import Request
from jwt import PyJWTError

from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.exception.user import InactiveUserError
from backend.domain.entity.user import User
from backend.domain.misc_types import Role
from backend.infrastructure.auth.access_token import AccessToken
from backend.infrastructure.auth.exception import UnauthorizedError
from backend.infrastructure.auth.idp.token_parser import AccessTokenParser
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor

TOKEN_TYPE = "Bearer"  # noqa: S105
BEARER_SECTIONS = 2
AUTH_HEADER = "Authorization"


@dataclass(slots=True, frozen=True)
class FastAPITokenParser(AccessTokenParser):
    request: Request
    processor: AccessTokenProcessor

    def parse_token(self) -> AccessToken:
        auth_header = self.request.headers.get(AUTH_HEADER)

        if auth_header is None:
            raise UnauthorizedError

        sections = auth_header.split()
        if len(sections) != BEARER_SECTIONS:
            raise UnauthorizedError

        token_type, token = sections

        if token_type != TOKEN_TYPE:
            raise UnauthorizedError

        try:
            decoded_token = self.processor.decode(token)
        except PyJWTError as e:
            raise UnauthorizedError from e

        access_token = AccessToken(
            user_id=decoded_token["sub"],
            role=Role(decoded_token["role"]),
            token=token,
            expires_in=datetime.fromtimestamp(decoded_token["exp"], tz=UTC),
            created_at=datetime.fromtimestamp(decoded_token["iat"], tz=UTC),
        )
        return access_token


@dataclass(slots=True)
class WebUserIdProvider(UserIdProvider):
    token_parser: AccessTokenParser
    gateway: UserGateway
    user: User | None = field(init=False, repr=False, default=None)

    async def get_user(self) -> User:
        if self.user is None:
            token_data = self.token_parser.parse_token()
            user = await self.gateway.get_by_id(token_data.user_id)

            if user is None:
                raise UnauthorizedError

            if user.is_active is False:
                raise InactiveUserError

            self.user = user

        return self.user

    async def get_user_or_none(self) -> User | None:
        try:
            return await self.get_user()
        except UnauthorizedError:
            return None
