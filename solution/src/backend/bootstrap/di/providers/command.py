from dishka import Provider, Scope, provide, provide_all

from backend.application.user.create import CreateUser
from backend.presentation.web.controller.login import WebLogin
from backend.presentation.web.controller.registration import WebRegistration


class CommandProvider(Provider):
    scope = Scope.REQUEST

    create_user = provide(CreateUser, scope=Scope.REQUEST)

    commands = provide_all(
        WebRegistration,
        WebLogin,
    )
