from dishka import Provider, Scope, WithParents, provide_all

from backend.infrastructure.database.gateway.fraud_rule import SAFraudRuleGateway
from backend.infrastructure.database.gateway.user import SAUserGateway


class GatewayProvider(Provider):
    scope = Scope.REQUEST

    gateways = provide_all(
        WithParents[SAUserGateway],
        WithParents[SAFraudRuleGateway],
    )
