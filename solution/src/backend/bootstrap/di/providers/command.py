from backend.application.user.create import CreateUser
from backend.application.user.read import ReadUser
from backend.presentation.web.controller.registration import WebRegistration
from dishka import Provider, Scope, provide, provide_all


class CommandProvider(Provider):
    scope = Scope.REQUEST

    # create_user = provide(CreateUser, scope=Scope.REQUEST)

    # commands = provide_all(
    #     ReadUser,
    #     WebRegistration,
    # )
