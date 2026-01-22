from dishka import Provider, Scope, provide

from backend.infrastructure.config_loader import (
    AdminConfig,
    Config,
    DataBaseConfig,
    JWTConfig,
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
    def admin(self, config: Config) -> AdminConfig:
        return config.admin

    @provide
    def redis(self, config: Config) -> RedisConfig:
        return config.redis

    @provide
    def jwt(self, config: Config) -> JWTConfig:
        return config.jwt
