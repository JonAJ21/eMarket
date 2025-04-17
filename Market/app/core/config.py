from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_connection: PostgresDsn = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        alias="POSTGRES_CONNECTION",
        json_schema_extra={"env": "POSTGRES_CONNECTION"},
    )
    echo: bool = Field(
        False,
        alias="ECHO",
        json_schema_extra={"env": "ECHO"},
    )
    
    jwt_secret_key: str = Field(
        "secret",
        alias="JWT_SECRET_KEY",
        json_schema_extra={"env": "JWT_SECRET_KEY"},
    )
    
    jwt_algorithm: str = Field(
        "HS256",
        alias="JWT_ALGORITHM",
        json_schema_extra={"env": "JWT_ALGORITHM"},
    )
    
    access_token_expire_minutes: int = Field(
        30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"},
    )
    
    refresh_token_expire_minutes: int = Field(
        60 * 24 * 7,
        alias="REFRESH_TOKEN_EXPIRE_MINUTES",
        json_schema_extra={"env": "REFRESH_TOKEN_EXPIRE_MINUTES"},
    )
    
    csrf_token_expire_minutes: int = Field(
        30,
        alias="CSRF_TOKEN_EXPIRE_MINUTES",
        json_schema_extra={"env": "CSRF_TOKEN_EXPIRE_MINUTES"},
    )
    
    csrf_token_length: int = Field(
        32,
        alias="CSRF_TOKEN_LENGTH",
        json_schema_extra={"env": "CSRF_TOKEN_LENGTH"},
    )
    
    
    
settings = Settings()