from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleEvaluationResultGateway
from backend.application.common.gateway.transaction import TransactionGateway
from backend.application.common.idp import UserIdProvider
from backend.application.exception.base import CustomValidationError, ForbiddenError
from backend.application.exception.transaction import (
    TransactionDoesNotExistError,
)
from backend.application.forms.transaction import ManyTransactionReadForm
from backend.application.transaction.dto import (
    FraudRuleEvaluationResultDTO,
    TransactionDecision,
    TransactionsList,
)
from backend.domain.misc_types import Role


@interactor
class ReadTransaction:
    idp: UserIdProvider
    transaction_gateway: TransactionGateway
    rule_result_gateway: FraudRuleEvaluationResultGateway

    async def execute(self, id: UUID) -> TransactionDecision:
        viewer = await self.idp.get_user()

        transaction = await self.transaction_gateway.get_by_id(id)

        if transaction is None:
            raise TransactionDoesNotExistError

        if transaction.user_id != viewer.id and viewer.role != Role.ADMIN:
            raise ForbiddenError

        rule_results = list(await self.rule_result_gateway.get_many(transaction_id=id))

        rule_results_dto = [
            FraudRuleEvaluationResultDTO(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                priority=result.priority,
                matched=result.matched,
                description=result.description,
            )
            for result in rule_results
        ]

        return TransactionDecision(transaction=transaction, rule_results=rule_results_dto)


@interactor
class ReadTransactions:
    gateway: TransactionGateway
    idp: UserIdProvider

    async def execute(self, form: ManyTransactionReadForm) -> TransactionsList:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            form.user_id = viewer.id

        if form.from_ > form.to:
            raise CustomValidationError(field="from", rejected_value=form.from_, issue="Некорректный from")

        if (form.to - form.from_).days > 90:
            raise CustomValidationError(
                field="to",
                rejected_value=form.to,
                issue="Слишком большой интервал дат",
            )

        offset = form.page * form.size

        transactions = await self.gateway.get_many(
            offset=offset,
            size=form.size,
            from_=form.from_,
            to=form.to,
            user_id=form.user_id,
            status=form.status,
            is_fraud=form.is_fraud,
        )
        total = await self.gateway.get_count(
            from_=form.from_,
            to=form.to,
            user_id=form.user_id,
            status=form.status,
            is_fraud=form.is_fraud,
        )

        return TransactionsList(items=list(transactions), total=total or 0, page=form.page, size=form.size)
