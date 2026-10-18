from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int = Field(default=5432, ge=1, le=65535)
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    JWT_SECRET_KEY: str = Field(min_length=64)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    ALGORITHM: Literal["HS256"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )
