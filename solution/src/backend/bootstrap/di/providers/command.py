from dishka import Provider, Scope, provide_all

from backend.application.user.create import CreateUser
from backend.application.user.read import ReadUser
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
        ReadUser,
        UpdateUser,
    )
