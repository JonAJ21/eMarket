from typing import List
from pydantic import EmailStr, Field, PostgresDsn, AnyHttpUrl
from pydantic_settings import BaseSettings
from async_fastapi_jwt_auth import AuthJWT

class Settings(BaseSettings):
    # MongoDB settings
    mongodb_url: str = Field(
        "",
        alias="MONGODB_URL",
        json_schema_extra={"env": "MONGODB_URL"}
    )
    mongodb_db_name: str = Field(
        "",
        alias="MONGODB_DB_NAME",
        json_schema_extra={"env": "MONGODB_DB_NAME"}
    )
    mongodb_username: str | None = Field(
        "",
        alias="MONGODB_USERNAME",
        json_schema_extra={"env": "PMONGODB_USERNAME"}
    )
    mongodb_password: str | None = Field(
        "",
        alias="MONGODB_PASSWORD",
        json_schema_extra={"env": "MONGODB_PASSWORD"}
    )

    # Redis settings
    redis_db: int = 0
    redis_host: str = Field(
        "redis_database",
        alias="REDIS_HOST",
        json_schema_extra={"env": "REDIS_HOST"},
    )
    redis_port: int = Field(
        6379,
        alias="REDIS_PORT",
        json_schema_extra={"env": "REDIS_PORT"},
    )
    redis_password: str = Field(
        "password",
        alias="REDIS_PASSWORD",
        json_schema_extra={"env": "REDIS_PASSWORD"},
    )

    # Server settings
    debug: bool = False
    api_v1_prefix: str = Field(
        "/api/v1",
        alias="API_V1_PREFIX",
        json_schema_extra={"env": "API_V1_PREFIX"},
    )
    project_name: str = Field(
        "Market",
        alias="PROJECT_NAME",
        json_schema_extra={"env": "PROJECT_NAME"},
    )
    backend_cors_origins: List[AnyHttpUrl] = []

    # PostgreSQL settings
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

    authjwt_secret_key: str = Field(
        "secret",
        alias="AUTHJWT_SECRET_KEY",
        json_schema_extra={"env": "AUTHJWT_SECRET_KEY"},
    )
    authjwt_access_token_expires: int = Field(
        900,
        alias="JWT_ACCESS_EXP_TIME",
        json_schema_extra={"env": "JWT_ACCESS_EXP_TIME"},
    )
    authjwt_refresh_token_expires: int = Field(
        86400,
        alias="JWT_REFRESH_EXP_TIME",
        json_schema_extra={"env": "JWT_REFRESH_EXP_TIME"},
    )

    authjwt_denylist_enabled: bool = False
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_same_site: str = "lax"

    super_user_login: str = Field(
        "superuser",
        alias="SUPER_USER_LOGIN",
        json_schema_extra={"env": "SUPER_USER_LOGIN"},
    )
    super_user_password: str = Field(
        "password",
        alias="SUPER_USER_PASSWORD",
        json_schema_extra={"env": "SUPER_USER_PASSWORD"},
    )
    super_user_email: EmailStr = Field(
        "superuser@example.com",
        alias="SUPER_USER_EMAIL",
        json_schema_extra={"env": "SUPER_USER_EMAIL"},
    )

    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        "kafka:29092", alias="KAFKA_BOOTSTRAP_SERVERS",
        json_schema_extra={"env": "KAFKA_BOOTSTRAP_SERVERS"},
    )
    KAFKA_ORDERS_TOPIC: str = Field(
        "dim_orders", alias="KAFKA_ORDERS_TOPIC",
        json_schema_extra={"env": "KAFKA_ORDERS_TOPIC"},
    )
    KAFKA_SALES_TOPIC: str = Field(
        "fact_sales", alias="KAFKA_SALES_TOPIC",
        json_schema_extra={"env": "KAFKA_SALES_TOPIC"},
    )

    YOOKASSA_SHOP_ID: str = Field(
        "", 
        alias="YOOKASSA_SHOP_ID",
        json_schema_extra={"env": "YOOKASSA_SHOP_ID"},
    )
    YOOKASSA_SECRET_KEY: str = Field(
        "", 
        alias="YOOKASSA_SECRET_KEY",
        json_schema_extra={"env": "YOOKASSA_SECRET_KEY"},
    )

    mongo_uri: str = Field(
        "mongodb://localhost:27017/market_db",
        alias="MONGODB_URI",
        json_schema_extra={"env": "MONGODB_URL"},
    )

settings = Settings()

@AuthJWT.load_config
def get_config():
    return settings
