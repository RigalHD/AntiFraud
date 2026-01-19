from collections.abc import Sequence

from backend.application.common.decorator import interactor
from backend.domain.entity.user import User


@interactor
class Users:
    users: Sequence[User]
    total_users_count: int
