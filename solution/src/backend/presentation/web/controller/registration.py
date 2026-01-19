from dataclasses import dataclass

from backend.application.forms.user import UserForm
from backend.application.user.create import CreateUser


@dataclass(slots=True, frozen=True)
class WebRegistration:
    create_user: CreateUser

    async def execute(self, form: UserForm) -> None:
        await self.create_user.execute(form)
