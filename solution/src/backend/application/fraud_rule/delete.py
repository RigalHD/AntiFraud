from uuid import UUID

from backend.application.common.decorator import interactor
from backend.application.common.gateway.fraud_rule import FraudRuleGateway
from backend.application.common.idp import UserIdProvider
from backend.application.common.uow import UoW
from backend.application.exception.base import ForbiddenError
from backend.application.exception.fraud_rule import FraudRuleDoesNotExistError
from backend.domain.misc_types import Role


@interactor
class DeleteFraudRule:
    idp: UserIdProvider
    gateway: FraudRuleGateway
    uow: UoW

    async def execute(self, id: UUID) -> None:
        viewer = await self.idp.get_user()

        if viewer.role != Role.ADMIN:
            raise ForbiddenError

        if not (fraud_rule := await self.gateway.get_by_id(id)):
            raise FraudRuleDoesNotExistError

        fraud_rule.enabled = False

        await self.uow.commit()
