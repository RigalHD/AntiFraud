from enum import Enum

from backend.presentation.web.controller.login import LoginResponse


class TestField(Enum):
    USE_DEFAULT = "USE_DEFAULT"
    CHANGE_IN_TEST = "CHANGE_IN_TEST"


class DictResult:
    NOT_FOUND = "NOT_FOUND"


type AuthorizedUser = LoginResponse
