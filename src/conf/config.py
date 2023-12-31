from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'postgresql+asyncpg://username:password@localhost:1234/db'
    SECRET_KEY_JWT: str = '123456789'
    SECRET_KEY_AUTH: str = '123456789'
    ALGORITHM: str = 'HS256'
    MAIL_USERNAME: str = 'postgres@mail.com'
    MAIL_PASSWORD: str = 'postgres'
    MAIL_FROM: str = 'postgres'
    MAIL_PORT: int = 465
    MAIL_SERVER: str = 'postgres'
    REDIS_DOMAIN: str = 'postgres'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = 'cloudinary'
    CLD_API_KEY: int = 599347874613237
    CLD_API_SECRET: str = 'secret'

    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, value):
        if value not in ['HS256', 'HS512']:
            raise ValueError('Algorithm must be HS256 or HS512')
        return value

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
