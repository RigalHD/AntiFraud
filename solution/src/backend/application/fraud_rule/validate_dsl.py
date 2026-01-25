from dataclasses import dataclass

from backend.application.common.decorator import interactor
from backend.application.common.exception_info import DSL_ERRORS_CODES
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.fraud_rule.dto import DSLErrorInfo
from backend.domain.exception.dsl import DSLError, DSLParseError
from backend.domain.misc_types import Role
from backend.domain.service.dsl.lex import Lexer
from backend.domain.service.dsl.normalize import ast_to_string
from backend.domain.service.dsl.parser import DSLParser
from backend.domain.service.dsl.validation import validate_dsl


@dataclass(slots=True, frozen=True)
class DSLInfo:
    is_valid: bool
    normalized_expression: str | None
    errors: list[DSLErrorInfo]


@interactor
class ValidateDSL:
    uow: UoW
    idp: UserIdProvider

    async def execute(self, dsl_expression: str) -> DSLInfo:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        try:
            validate_dsl(dsl_expression)
        except DSLError:
            return DSLInfo(
                is_valid=False,
                normalized_expression=None,
                errors=[],
            )

        is_valid = False
        normalized_expression = None
        errors: list[DSLErrorInfo] = []

        try:
            tokens = Lexer(dsl_expression).tokenize()
            ast = DSLParser(tokens).parse()
        except DSLError as e:
            code = DSL_ERRORS_CODES[type(e)]
            message = e.message
            position = None
            near = None
            if isinstance(e, DSLParseError):
                position = e.position
                near = e.near

            error_info = DSLErrorInfo(
                code=code,
                message=message,
                position=position,
                near=near,
            )

            errors.append(error_info)
        else:
            is_valid = True
            normalized_expression = ast_to_string(ast)

        dsl_info = DSLInfo(
            is_valid=is_valid,
            normalized_expression=normalized_expression,
            errors=errors,
        )

        return dsl_info
