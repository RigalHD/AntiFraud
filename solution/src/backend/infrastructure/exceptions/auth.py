from backend.application.exception.base import ApplicationError


class UnauthenticatedError(ApplicationError): ...


class UnauthorizedError(ApplicationError): ...
