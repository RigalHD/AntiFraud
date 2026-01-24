from dishka import Provider, Scope, WithParents, provide_all

from backend.infrastructure.database.gateway.fraud_rule import SAFraudRuleEvaluationResultGateway, SAFraudRuleGateway
from backend.infrastructure.database.gateway.transaction import SATransactionGateway
from backend.infrastructure.database.gateway.user import SAUserGateway


class GatewayProvider(Provider):
    scope = Scope.REQUEST

    gateways = provide_all(
        WithParents[SAUserGateway],
        WithParents[SAFraudRuleGateway],
        WithParents[SAFraudRuleEvaluationResultGateway],
        WithParents[SATransactionGateway],
    )
