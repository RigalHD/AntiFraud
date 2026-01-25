from decimal import Decimal

from backend.domain.entity.transaction import Transaction
from backend.domain.exception.dsl import DSLError, DSLInvalidFieldError, DSLInvalidOperatorError
from backend.domain.service.dsl.ast_node import ASTNode, Comparison, Logical


class DSLEvaluator:
    def __init__(self, transaction: Transaction) -> None:
        self.context = {
            "amount": transaction.amount,
            "currency": f"'{transaction.currency}'",
            "merchantId": f"'{transaction.merchant_id}'",
            "ipAddress": f"'{transaction.ip_address}'",
            "deviceId": f"'{transaction.device_id}'",
        }

    def eval_logical(self, node: Logical) -> bool:
        left = self.eval(node.left)
        right = self.eval(node.right)

        if node.operator == "AND":
            return left and right

        if node.operator == "OR":
            return left or right

        raise ValueError("Unknown logical operator " + node.operator)

    def eval_comparison(self, node: Comparison) -> bool:  # noqa: PLR0911
        left = self.context[node.left]
        right = node.right

        if node.left not in self.context:
            raise DSLInvalidFieldError(message=f"Поле отсутствует внутри контекста: {node.left}")

        if isinstance(left, str) and isinstance(right, str):
            match node.operator:
                case "=":
                    return left.strip("'") == right.strip("'")
                case "!=":
                    return left.strip("'") != right.strip("'")

        if isinstance(left, (int, Decimal)) and isinstance(right, (int, Decimal)):
            match node.operator:
                case "=":
                    return left == right
                case "!=":
                    return left != right
                case ">":
                    return left > right
                case "<":
                    return left < right
                case ">=":
                    return left >= right
                case "<=":
                    return left <= right

        raise DSLInvalidOperatorError(message="Подходящий оператор сравнения не найден")

    def eval(self, node: ASTNode) -> bool:
        if isinstance(node, Logical):
            return self.eval_logical(node)

        if isinstance(node, Comparison):
            return self.eval_comparison(node)

        raise DSLError(message="Неизвестный ASTNode")
