from dataclasses import dataclass

from backend.application.common.decorator import interactor
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import DSLError
from backend.domain.misc_types import Role
from backend.domain.service.dsl import is_dsl_valid, normalize_dsl


@dataclass(slots=True, frozen=True)
class DSLInfo:
    is_valid: bool
    normalized_expression: str | None
    errors: list[DSLError]


@interactor
class ValidateDSL:
    uow: UoW
    idp: UserIdProvider

    async def execute(self, dsl_expression: str, temp_validate_anyway: bool = False) -> DSLInfo:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        is_valid = is_dsl_valid(dsl_expression)
        normalized_expression = None
        errors: list[DSLError] = []  # Реализовать логику добавления ошибок

        if temp_validate_anyway:
            is_valid = True

        if is_valid:
            normalized_expression = normalize_dsl(dsl_expression)

        dsl_info = DSLInfo(is_valid=is_valid, normalized_expression=normalized_expression, errors=errors)

        return dsl_info
