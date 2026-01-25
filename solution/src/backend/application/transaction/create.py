from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.gateway.transaction import TransactionGateway
from backend.application.common.gateway.user import UserGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import CustomValidationError, ForbiddenError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.forms.transaction import TransactionForm
from backend.application.service.rule_evaluator import RuleEvaluator
from backend.application.transaction.dto import FraudRuleEvaluationResultDTO, TransactionDecision
from backend.domain.entity.transaction import Transaction, TransactionLocation
from backend.domain.misc_types import Role, TransactionStatus


@interactor
class CreateTransaction:
    uow: UoW
    gateway: TransactionGateway
    rule_gateway: FraudRuleGateway
    idp: UserIdProvider
    user_gateway: UserGateway
    rule_evaluator: RuleEvaluator

    async def execute(self, form: TransactionForm) -> TransactionDecision:
        viewer = await self.idp.get_user()

        if viewer.is_active is False:
            raise ForbiddenError

        if viewer.role == Role.USER:
            user_id = viewer.id
        else:
            if form.user_id is None:
                raise CustomValidationError(field="userId", rejected_value=None, issue="UserId Отсуствует")
            user_id = form.user_id

        if await self.user_gateway.get_by_id(user_id) is None:
            raise UserDoesNotExistError

        location = TransactionLocation(
            country=form.location.country,
            city=form.location.city,
            latitude=form.location.latitude,
            longitude=form.location.longitude,
        )

        rounded_amount = form.amount.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

        if form.timestamp > (datetime.now(tz=UTC) + timedelta(minutes=5)):
            raise CustomValidationError(
                field="timestamp",
                rejected_value=form.timestamp,
                issue="Транзакция из далекого будущего",
            )

        transaction = Transaction(
            id=uuid4(),
            user_id=user_id,
            amount=rounded_amount,
            currency=form.currency,
            status=TransactionStatus.APPROVED,
            merchant_id=form.merchant_id,
            merchant_category_code=form.merchant_category_code,
            timestamp=form.timestamp,
            ip_address=form.ip_address,
            device_id=form.device_id,
            channel=form.channel,
            location=location,
            metadata=form.metadata,
            is_fraud=False,
        )

        evaluator_result = await self.rule_evaluator.execute(transaction)

        rule_results_dto = [
            FraudRuleEvaluationResultDTO(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                priority=result.priority,
                matched=result.matched,
                description=result.description,
            )
            for result in evaluator_result.rule_results
        ]

        transaction.is_fraud = evaluator_result.is_fraud
        transaction.status = evaluator_result.status

        self.uow.add(transaction)
        await self.uow.flush((transaction,))

        for rule_result in evaluator_result.rule_results:
            self.uow.add(rule_result)
        await self.uow.flush((*evaluator_result.rule_results,))

        await self.uow.commit()

        transaction_decision = TransactionDecision(
            transaction=transaction,
            rule_results=rule_results_dto,
        )

        return transaction_decision
