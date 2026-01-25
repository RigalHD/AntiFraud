from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import ValidationError

from backend.application.exception.base import (
    ApplicationError,
    CustomValidationError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from backend.application.exception.fraud_rule import (
    FraudRuleDoesNotExistError,
    FraudRuleNameAlreadyExistsError,
)
from backend.application.exception.transaction import (
    MissingLonOrLatError,
    TransactionDoesNotExistError,
)
from backend.application.exception.user import (
    EmailAlreadyExistsError,
    InactiveUserError,
    UserDoesNotExistError,
)
from backend.domain.exception.dsl import (
    DSLError,
    DSLInvalidFieldError,
    DSLInvalidOperatorError,
    DSLParseError,
)
from backend.infrastructure.api.exception import (
    InternalServerError,
    StatusMismatchError,
    UnableToUnwrapError,
)
from backend.infrastructure.parser.pydantic_error import FieldErrorInfo
from backend.infrastructure.serialization.base import FieldSkip

ERROR_HTTP_CODE = {
    ApplicationError: 500,
    ForbiddenError: 403,
    NotFoundError: 404,
    EmailAlreadyExistsError: 409,
    UserDoesNotExistError: 404,
    UnauthorizedError: 401,
    JSONDecodeError: 400,
    InactiveUserError: 423,
    ValidationError: 422,
    InternalServerError: 500,
    FraudRuleNameAlreadyExistsError: 409,
    FraudRuleDoesNotExistError: 404,
    DSLError: 422,
    DSLParseError: 422,
    DSLInvalidFieldError: 422,
    DSLInvalidOperatorError: 422,
    MissingLonOrLatError: 422,
    TransactionDoesNotExistError: 404,
    CustomValidationError: 422,
}

ERROR_MESSAGE = {
    ApplicationError: "Ошибка приложения",
    InternalServerError: "Внутренняя ошибка сервера",
    NotFoundError: "Ресурс не найден",
    ForbiddenError: "Недостаточно прав для выполнения операции",
    EmailAlreadyExistsError: "Токен отсутствует/невалиден/истёк; неверный email или пароль в /auth/login",
    UserDoesNotExistError: "Ресурс не найден",
    UnauthorizedError: "Токен отсутствует или невалиден",
    JSONDecodeError: "Невалидный JSON, неподдерживаемый Content-Type",
    InactiveUserError: "Пользователь деактивирован",
    ValidationError: "Некоторые поля не прошли валидацию",
    FraudRuleNameAlreadyExistsError: "Правило с таким именем уже существует",
    FraudRuleDoesNotExistError: "Ресурс не найден",
    DSLError: "Ошибка в DSL выражении",
    DSLParseError: "Синтаксическая ошибка",
    DSLInvalidFieldError: "Неизвестное поле DSL",
    DSLInvalidOperatorError: "Оператор неприменим к типу",
    MissingLonOrLatError: "Некоторые поля не прошли валидацию",
    TransactionDoesNotExistError: "Ресурс не найден",
    CustomValidationError: "Некоторые поля не прошли валидацию",
}

ERROR_CODE = {
    ApplicationError: "UNHANDLED",
    InternalServerError: "INTERNAL_SERVER_ERROR",
    ForbiddenError: "FORBIDDEN",
    NotFoundError: "NOT_FOUND",
    EmailAlreadyExistsError: "EMAIL_ALREADY_EXISTS",
    UserDoesNotExistError: "NOT_FOUND",
    UnauthorizedError: "UNAUTHORIZED",
    JSONDecodeError: "BAD_REQUEST",
    InactiveUserError: "USER_INACTIVE",
    ValidationError: "VALIDATION_FAILED",
    FraudRuleNameAlreadyExistsError: "RULE_NAME_ALREADY_EXISTS",
    FraudRuleDoesNotExistError: "NOT_FOUND",
    DSLError: "DSL_ERROR",
    DSLParseError: "DSL_PARSE_ERROR",
    DSLInvalidFieldError: "DSL_INVALID_FIELD",
    DSLInvalidOperatorError: "DSL_INVALID_OPERATOR",
    MissingLonOrLatError: "VALIDATION_FAILED",
    TransactionDoesNotExistError: "NOT_FOUND",
    CustomValidationError: "VALIDATION_FAILED",
}

DETAILS: dict[type[Exception], dict[str, str | int]] = {
    JSONDecodeError: {"hint": "Проверьте запятые/кавычки"},
}


@dataclass(slots=True)
class ApiErrorResponse:
    # Обязательно при инициализации нужно отрезать слеш в конце path
    code: str
    message: str
    timestamp: datetime
    path: str
    trace_id: UUID
    details: dict[str, str | int] | FieldSkip = FieldSkip.SKIP
    field_errors: list[FieldErrorInfo] | FieldSkip = FieldSkip.SKIP

    @staticmethod
    def generate_default(exc_type: type[Exception], path: str) -> ApiErrorResponse:
        return ApiErrorResponse(
            code=ERROR_CODE[exc_type],
            message=ERROR_MESSAGE[exc_type],
            trace_id=uuid4(),
            timestamp=datetime.now(tz=UTC),
            path=path.rstrip("/"),
            details=DETAILS.get(exc_type, FieldSkip.SKIP),
        )


@dataclass(slots=True, frozen=True)
class HttpResponse:
    status: int
    url: str


@dataclass(slots=True, frozen=True)
class PingResponse:
    status: Literal["ok"]


@dataclass(slots=True, frozen=True)
class UnwrappedErrorData:
    http_response: HttpResponse
    error_data: ApiErrorResponse


@dataclass(slots=True, frozen=True)
class APIResponse[T]:
    data: T | None
    http_response: HttpResponse
    error_data: ApiErrorResponse | None

    def expect_status(self, expected_status: int) -> Self:
        if (response_status := self.http_response.status) != expected_status:
            message = f"Ожидаемый статус: {expected_status}, полученный: {response_status}"
            raise StatusMismatchError(message)

        return self

    def unwrap(self) -> T:
        if self.data is not None and self.error_data is None:
            return self.data

        raise UnableToUnwrapError

    def err_unwrap(self) -> UnwrappedErrorData:
        if self.data is None and self.error_data is not None:
            return UnwrappedErrorData(
                http_response=self.http_response,
                error_data=self.error_data,
            )

        raise UnableToUnwrapError
