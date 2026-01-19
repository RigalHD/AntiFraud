from uuid import uuid4

from backend.application.common.auth_provider import AuthProvider
from backend.application.common.decorator import interactor
from backend.application.common.uow import UoW
from backend.application.forms.user import UserForm
from backend.domain.entity.user import User
from backend.infrastructure.auth.hasher import Hasher


@interactor
class CreateUser:
    uow: UoW
    hasher: Hasher
    
    async def execute(self, form: UserForm) -> User:
        hashed_password = self.hasher.hash(form.password)

        user = User(
            user_id=uuid4(),
            email=form.email,
            password=hashed_password,
            full_name=form.full_name,
            age=form.age,
            region=form.region,
            gender=form.gender,
            marital_status=form.marital_status,
            role=form.role,
        )

        self.uow.add(user)
        await self.uow.flush((user,))
        await self.uow.commit()

        return user