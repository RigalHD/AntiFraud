from dataclasses import dataclass

from backend.domain.entity.user import User


@dataclass(slots=True, frozen=True)
class Users:
    items: list[User]
    total: int
    page: int
    size: int
