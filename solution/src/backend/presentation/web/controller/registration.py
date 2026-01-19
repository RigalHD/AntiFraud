from dataclasses import dataclass

from backend.application.forms.user import UserForm
from backend.application.user.create import CreateUser
from backend.domain.entity.user import User
from dishka.container import ContextWrapper


@dataclass(slots=True, frozen=True)
class WebRegistration:
    create_user: CreateUser

    def execute(self, form: UserForm) -> User:
        return self.create_user.execute(form)
