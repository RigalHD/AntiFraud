from enum import Enum
from typing import Protocol


class Permissions(Protocol, Enum):
    @classmethod
    def values(cls) -> list[int]:
        return [item.value for item in cls]