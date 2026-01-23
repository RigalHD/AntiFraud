from dishka import Provider, Scope, provide_all

from backend.application.fraud_rule.create import CreateFraudRule
from backend.application.fraud_rule.delete import DeleteFraudRule
from backend.application.fraud_rule.read import ReadFraudRule, ReadFraudRules
from backend.application.fraud_rule.update import UpdateFraudRule
from backend.application.fraud_rule.validate_dsl import ValidateDSL
from backend.application.user.create import CreateAdminUser, CreateUser
from backend.application.user.delete import DeleteUser
from backend.application.user.read import ReadUser, ReadUsers
from backend.application.user.update import UpdateUser
from backend.presentation.web.controller.login import WebLogin
from backend.presentation.web.controller.registration import WebRegistration


class CommandProvider(Provider):
    scope = Scope.REQUEST

    controllers = provide_all(
        WebRegistration,
        WebLogin,
    )

    commands = provide_all(
        CreateUser,
        CreateAdminUser,
        ReadUser,
        ReadUsers,
        UpdateUser,
        DeleteUser,
        CreateFraudRule,
        ReadFraudRule,
        ReadFraudRules,
        UpdateFraudRule,
        DeleteFraudRule,
        ValidateDSL,
    )
