from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from backend.domain.exception.dsl import (
    DSLInvalidFieldError,
    DSLInvalidOperatorError,
    DSLParseError,
)
from backend.domain.service.dsl.ast_node import ASTNode, Comparison, Logical
from backend.domain.service.dsl.tokens import Token, TokenType

VALID_FIELDS = {"amount", "currency", "merchantId", "ipAddress", "deviceId"}
STRING_FIELDS = {"currency", "ipAddress", "deviceId", "merchantId"}
DECIMAL_FIELDS = {"amount"}
NUMERIC_OPERATORS = {"=", "!=", "<", "<=", ">", ">="}


@dataclass(slots=True)
class DSLParser:
    tokens: list[Token]
    pos: int = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def next(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse_value(self, token: Token) -> Decimal | int | str:
        if token.token_type == TokenType.NUMBER:
            try:
                if "." not in token.value:
                    return int(token.value)
                return Decimal(token.value)
            except InvalidOperation:
                raise DSLParseError(
                    message="Некорректное числовое значение",
                    position=token.pos,
                    near=token.value,
                ) from InvalidOperation

        if token.token_type == TokenType.STRING:
            return token.value.strip("'")

        return token.value

    def parse_comparison(self) -> ASTNode:
        left = self.next()
        operator = self.next()
        right = self.next()

        if left.token_type != TokenType.FIELD:
            raise DSLParseError(message="Ошибка парсинга", position=left.pos, near=left.value)
        if operator.token_type != TokenType.OP:
            raise DSLParseError(
                message="Ошибка парсинга",
                position=operator.pos,
                near=operator.value,
            )
        if right.token_type not in (TokenType.NUMBER, TokenType.STRING):
            raise DSLParseError(
                message="Ошибка парсинга",
                position=right.pos,
                near=right.value,
            )

        if left.value not in VALID_FIELDS:
            raise DSLInvalidFieldError(message=f"Поле неподдерживается: {left.value}")

        if (
            left.value in STRING_FIELDS and operator.value not in ("=", "!=")
        ) or operator.value not in NUMERIC_OPERATORS:
            raise DSLInvalidOperatorError(message=f"Неподдерживаемая операция {operator.value}")

        right_value = self.parse_value(right)

        if left.value not in STRING_FIELDS and not isinstance(right_value, (int, Decimal)):
            raise DSLInvalidOperatorError(message=f"Неподдерживаемая операция {operator.value}")

        return Comparison(
            left=left.value,
            operator=operator.value,
            right=right_value,
        )

    def parse_and(self) -> ASTNode:
        node = self.parse_comparison()

        while self.current.token_type == TokenType.AND:
            operator = self.next().value
            right = self.parse_comparison()
            node = Logical(node, operator, right)

        return node

    def parse_or(self) -> ASTNode:
        node = self.parse_and()

        while self.current.token_type == TokenType.OR:
            operator = self.next().value
            right = self.parse_and()
            node = Logical(node, operator, right)

        return node

    def parse(self) -> ASTNode:
        return self.parse_or()
