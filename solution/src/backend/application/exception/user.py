from dataclasses import dataclass

from backend.application.exception.base import ApplicationError


class UserDoesNotExistError(ApplicationError): ...


@dataclass
class EmailAlreadyExistsError(ApplicationError):
    email: str


class InactiveUserError(ApplicationError): ...
