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
    
    
settings = Settings()