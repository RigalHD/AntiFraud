from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.exception.base import ForbiddenError, InvalidPaginationQueryError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.user.dto import Users
from backend.domain.entity.user import User
from backend.domain.misc_types import Role


@interactor
class ReadUser:
    idp: UserIdProvider
    gateway: UserGateway

    async def execute(self, id: UUID | None = None) -> User:
        viewer = await self.idp.get_user()

        if id is None or id == viewer.id:
            return viewer

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

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
