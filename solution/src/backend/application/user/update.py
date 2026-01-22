from datetime import UTC, datetime
from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.forms.user import UpdateUserForm
from backend.domain.entity.user import User
from backend.domain.misc_types import Role


@interactor
class UpdateUser:
    idp: UserIdProvider
    gateway: UserGateway
    uow: UoW

    async def execute(self, form: UpdateUserForm, id: UUID | None = None) -> User:
        viewer = await self.idp.get_user()

        if (form.role is not None or form.is_active is not None) and viewer.role != Role.ADMIN:
            raise ForbiddenError

        if id is not None and id != viewer.id and viewer.role != Role.ADMIN:
            raise ForbiddenError

        if id is None or id == viewer.id:
            user = viewer
        else:
            if not (usr := await self.gateway.get_by_id(id)):
                raise UserDoesNotExistError

            user = usr

        user.full_name = form.full_name
        user.age = form.age
        user.region = form.region
        user.gender = form.gender
        user.marital_status = form.marital_status
        user.updated_at = datetime.now(tz=UTC)

        if form.role is not None:
            user.role = form.role

        if form.is_active is not None:
            user.is_active = form.is_active

        await self.uow.commit()

        return user
