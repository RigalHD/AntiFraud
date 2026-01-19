from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.exception.base import InvalidPaginationQueryError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.user.dto import Users
from backend.domain.entity.user import User


@interactor
class ReadUser:
    idp: UserIdProvider
    gateway: UserGateway

    async def execute(self, id: UUID) -> User:
        user = await self.gateway.get_by_id(id)

        if user is None:
            raise UserDoesNotExistError

        return user


@interactor
class ReadUsers:
    gateway: UserGateway
    idp: UserIdProvider

    async def execute(self, offset: int, limit: int, desc: bool = True) -> Users:
        if limit < 0 or offset < 0:
            raise InvalidPaginationQueryError

        users = await self.gateway.get_many(offset=offset, limit=limit, desc=desc)
        total_users_count = await self.gateway.get_count()

        return Users(users=users, total_users_count=total_users_count or 0)
