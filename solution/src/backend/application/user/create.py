from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.user import UserGateway
from backend.application.common.uow import UoW
from backend.application.exception.user import EmailAlreadyExistsError
from backend.application.forms.user import UserForm
from backend.domain.entity.user import User
from backend.infrastructure.auth.hasher import Hasher


@interactor
class CreateUser:
    uow: UoW
    hasher: Hasher
    gateway: UserGateway

    async def execute(self, form: UserForm) -> User:
        hashed_password = self.hasher.hash(form.password)

        if await self.gateway.get_by_email(form.email):
            raise EmailAlreadyExistsError(email=form.email)

        user = User(
            id=uuid4(),
            email=form.email,
            password=hashed_password,
            full_name=form.full_name,
            age=form.age,
            region=form.region,
            gender=form.gender,
            marital_status=form.marital_status,
        )

        self.uow.add(user)
        await self.uow.flush((user,))
        await self.uow.commit()

        return user
