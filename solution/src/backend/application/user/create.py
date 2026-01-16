from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.uow import UoW
from backend.domain.entity.user import User


@interactor
class CreateUser:
    uow: UoW

    async def execute(self) -> User:
        user = User(user_id=uuid4())

        self.uow.add(user)
        await self.uow.flush((user,))

        await self.uow.commit()

        return user
