from dataclasses import dataclass
from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.domain.entity.fraud_rule import FraudRuleEvaluationResult
from backend.domain.entity.transaction import Transaction
from backend.domain.exception.dsl import DSLError
from backend.domain.misc_types import TransactionStatus
from backend.domain.service.dsl.evaluate import DSLEvaluator
from backend.domain.service.dsl.lex import Lexer
from backend.domain.service.dsl.parser import DSLParser
from backend.domain.service.dsl.validation import validate_dsl


@dataclass(slots=True, frozen=True)
class RuleEvaluatorResult:
    status: TransactionStatus
    is_fraud: bool
    rule_results: list[FraudRuleEvaluationResult]


@interactor
class RuleEvaluator:
    rule_gateway: FraudRuleGateway

    async def execute(self, transaction: Transaction) -> RuleEvaluatorResult:
        rule_results: list[FraudRuleEvaluationResult] = []

        is_fraud = False
        status = TransactionStatus.APPROVED

        dsl_evaluator = DSLEvaluator(transaction=transaction)
        enabled_rules = list(await self.rule_gateway.get_many_by_priority(enabled=True))

        for rule in enabled_rules:
            try:
                validate_dsl(rule.dsl_expression)
                tokens = Lexer(rule.dsl_expression).tokenize()
                ast = DSLParser(tokens).parse()
                result = dsl_evaluator.eval(ast)
            except DSLError:
                result = False

            if result is True:
                is_fraud = True
                status = TransactionStatus.DECLINED

            description = f'Правило "{rule.dsl_expression}" {"сработало" if result else "не сработало"}'

            rule_result = FraudRuleEvaluationResult(
                id=uuid4(),
                transaction_id=transaction.id,
                rule_id=rule.id,
                rule_name=rule.name,
                priority=rule.priority,
                matched=result,
                description=description,
            )

            rule_results.append(rule_result)

        return RuleEvaluatorResult(
            status=status,
            is_fraud=is_fraud,
            rule_results=rule_results,
        )
