from dishka import Provider, Scope


class CommandProvider(Provider):
    scope = Scope.REQUEST

    # create_user = provide(CreateUser, scope=Scope.REQUEST)

    # commands = provide_all(
    #     ReadUser,
    #     ReadUsers,
    # )
