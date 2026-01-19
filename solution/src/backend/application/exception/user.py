from backend.application.exception.base import ApplicationError


class UserDoesNotExistError(ApplicationError): ...


class EmailAlreadyExistsError(ApplicationError): ...


class InactiveUserError(ApplicationError): ...
