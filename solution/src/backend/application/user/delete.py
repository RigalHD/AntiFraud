from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.user import UserDoesNotExistError
from backend.domain.misc_types import Role


@interactor
class DeleteUser:
    idp: UserIdProvider
    gateway: UserGateway
    uow: UoW

    async def execute(self, id: UUID) -> None:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        if not (user := await self.gateway.get_by_id(id)):
            raise UserDoesNotExistError

        user.is_active = False

        await self.uow.commit()
