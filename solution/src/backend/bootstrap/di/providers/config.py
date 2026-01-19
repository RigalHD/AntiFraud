from dishka import Provider, Scope, provide

from backend.infrastructure.config_loader import (
    Config,
    DataBaseConfig,
    JWTConfig,
    MiscConfig,
    RedisConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def config(self) -> Config:
        return Config.load_from_environment()

    @provide
    def db(self, config: Config) -> DataBaseConfig:
        return config.db

    @provide
    def redis(self, config: Config) -> RedisConfig:
        return config.redis

    @provide
    def misc(self, config: Config) -> MiscConfig:
        return config.misc

    @provide
    def jwt(self, config: Config) -> JWTConfig:
        return config.jwt
