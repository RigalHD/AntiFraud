from backend.application.exception.base import ApplicationError


class InternalServerError(ApplicationError): ...


class StatusMismatchError(Exception): ...


class UnableToUnwrapError(Exception): ...
