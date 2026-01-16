from backend.application.exception.base import ApplicationError


class UserDoesNotExistError(ApplicationError): ...


class UserAlreadyExistsError(ApplicationError): ...
