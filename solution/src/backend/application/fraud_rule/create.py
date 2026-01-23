from uuid import uuid4

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import DSLError, FraudRuleNameAlreadyExistsError
from backend.application.forms.fraud_rule import FraudRuleForm
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.misc_types import Role


@interactor
class CreateFraudRule:
    uow: UoW
    gateway: FraudRuleGateway
    idp: UserIdProvider
    dsl_validator: ValidateDSL

    async def execute(self, form: FraudRuleForm) -> FraudRule:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        if await self.gateway.get_by_name(form.name):
            raise FraudRuleNameAlreadyExistsError(name=form.name)

        dsl_info = await self.dsl_validator.execute(form.dsl_expression)

        if dsl_info.is_valid is False or dsl_info.normalized_expression is None:
            if len(dsl_info.errors) >= 1:
                raise dsl_info.errors[0]
            raise DSLError

        fraud_rule = FraudRule(
            id=uuid4(),
            name=form.name,
            description=form.description,
            dsl_expression=dsl_info.normalized_expression,
            priority=form.priority,
            enabled=form.enabled,
        )
        self.uow.add(fraud_rule)
        await self.uow.flush((fraud_rule,))
        await self.uow.commit()

        return fraud_rule
