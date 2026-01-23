from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.idp import UserIdProvider
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import FraudRuleDoesNotExistError
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.misc_types import Role


@interactor
class ReadFraudRule:
    idp: UserIdProvider
    gateway: FraudRuleGateway

    async def execute(self, id: UUID) -> FraudRule:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        fraud_rule = await self.gateway.get_by_id(id)

        if fraud_rule is None:
            raise FraudRuleDoesNotExistError

        return fraud_rule


@interactor
class ReadFraudRules:
    gateway: FraudRuleGateway
    idp: UserIdProvider

    async def execute(self) -> list[FraudRule]:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        fraud_rules = await self.gateway.get_many()

        return list(fraud_rules)
