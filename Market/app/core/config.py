from pydantic import EmailStr, Field, PostgresDsn
from pydantic_settings import BaseSettings
from async_fastapi_jwt_auth import AuthJWT
from typing import Optional

class Settings(BaseSettings):
    postgres_connection: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        alias="POSTGRES_CONNECTION"
    )
    echo: bool = Field(default=False, alias="ECHO")

    redis_host: str = Field(default="redis_database", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")

    authjwt_secret_key: str = Field(default="secret", alias="AUTHJWT_SECRET_KEY")
    authjwt_access_token_expires: int = Field(default=900, alias="JWT_ACCESS_EXP_TIME")
    authjwt_refresh_token_expires: int = Field(default=86400, alias="JWT_REFRESH_EXP_TIME")

    authjwt_denylist_enabled: bool = False
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_same_site: str = "lax"

    super_user_login: str = Field(default="superuser", alias="SUPER_USER_LOGIN")
    super_user_password: str = Field(default="password", alias="SUPER_USER_PASSWORD")
    super_user_email: EmailStr = Field(default="superuser@example.com", alias="SUPER_USER_EMAIL")

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_ORDERS_TOPIC: str = "dim_orders"
    KAFKA_SALES_TOPIC: str = "fact_sales"

    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str

    mongo_uri: str = Field(default="mongodb://localhost:27017/market_db", alias="MONGO_URI")

    class Config:
        env_file = ".env"

settings = Settings()

@AuthJWT.load_config
def get_config():
    return settings
