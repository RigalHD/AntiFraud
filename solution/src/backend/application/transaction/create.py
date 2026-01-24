from uuid import UUID, uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.gateway.transaction import TransactionGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.forms.transaction import TransactionForm
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.domain.entity.fraud_rule import FraudRuleEvaluationResult
from backend.domain.entity.transaction import Transaction, TransactionLocation
from backend.domain.exception.dsl import DSLError
from backend.domain.misc_types import Role
from backend.domain.service.dsl.evaluate import Evaluator
from backend.domain.service.dsl.lex import Lexer
from backend.domain.service.dsl.parser import DSLParser
from backend.domain.service.dsl.validation import validate_dsl


@interactor
class CreateTransaction:
    uow: UoW
    gateway: TransactionGateway
    rule_gateway: FraudRuleGateway
    idp: UserIdProvider
    dsl_validator: ValidateDSL

    async def execute(self, form: TransactionForm, user_id: UUID) -> Transaction:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN and user_id != viewer.id:
            raise ForbiddenError

        is_fraud = False
        location = TransactionLocation(
            country=form.location.country,
            city=form.location.city,
            latitude=form.location.latitude,
            longitude=form.location.longitude,
        )

        transaction = Transaction(
            id=uuid4(),
            user_id=user_id,
            amount=form.amount,
            currency=form.currency,
            status=form.status,
            merchant_id=form.merchant_id,
            merchant_category_code=form.merchant_category_code,
            timestamp=form.timestamp,
            ip_address=str(form.ip_address),
            device_id=form.device_id,
            channel=form.channel,
            location=location,
            metadata=form.metadata,
            is_fraud=is_fraud,
        )

        enabled_rules = list(await self.rule_gateway.get_many_by_priority(enabled=True))
        rule_results: list[FraudRuleEvaluationResult] = []

        evaluator = Evaluator(transaction=transaction)

        for rule in enabled_rules:
            try:
                validate_dsl(rule.dsl_expression)
                tokens = Lexer(rule.dsl_expression).tokenize()
                ast = DSLParser(tokens).parse()
                result = evaluator.eval(ast)
            except DSLError:
                result = False

            if result:
                is_fraud = True

            description = f'Правило "{rule.dsl_expression}" {"сработало" if result else "не сработало"}'

            rule_result = FraudRuleEvaluationResult(
                transaction_id=transaction.id,
                rule_id=rule.id,
                rule_name=rule.name,
                priority=rule.priority,
                matched=result,
                description=description,
            )
            self.uow.add(rule_result)
            rule_results.append(rule_result)

        transaction.is_fraud = is_fraud

        self.uow.add(transaction)
        await self.uow.flush((transaction, *rule_results))
        await self.uow.commit()

        return transaction
