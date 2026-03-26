from functools import cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    POSTGRES_USER: str = Field(default="user")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    LOG_DB_NAME: str = "log_db"

    LOG_MSERVICE_HTTP_HOST: str = "0.0.0.0"
    LOG_MSERVICE_HTTP_PORT: int = 8080

    LOG_MSERVICE_GRPC_HOST: str = "[::]"
    LOG_MSERVICE_GRPC_PORT: int = 50051

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.LOG_DB_NAME}"
        )


@cache
def get_settings() -> Settings:
    return Settings()
