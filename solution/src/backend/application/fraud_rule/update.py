from datetime import UTC, datetime
from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import (
    FraudRuleDoesNotExistError,
    FraudRuleNameAlreadyExistsError,
)
from backend.application.forms.fraud_rule import UpdateFraudRuleForm
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.misc_types import Role


@interactor
class UpdateFraudRule:
    idp: UserIdProvider
    gateway: FraudRuleGateway
    uow: UoW
    dsl_validator: ValidateDSL

    async def execute(self, form: UpdateFraudRuleForm, id: UUID) -> FraudRule:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        if not (fraud_rule := await self.gateway.get_by_id(id)):
            raise FraudRuleDoesNotExistError

        if (rule := (await self.gateway.get_by_name(form.name))) and rule.id != id:
            raise FraudRuleNameAlreadyExistsError(name=form.name)

        dsl_info = await self.dsl_validator.execute(form.dsl_expression)

        fraud_rule.name = form.name
        fraud_rule.description = form.description
        fraud_rule.dsl_expression = dsl_info.normalized_expression or form.dsl_expression
        fraud_rule.enabled = form.enabled
        fraud_rule.priority = form.priority
        fraud_rule.updated_at = datetime.now(tz=UTC)

        await self.uow.commit()

        return fraud_rule
