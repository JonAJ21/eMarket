from pydantic import EmailStr, Field, PostgresDsn
from pydantic_settings import BaseSettings
from async_fastapi_jwt_auth import AuthJWT

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
    
    
    authjwt_secret_key: str = Field(
        "secret",
        alias="AUTHJWT_SECRET_KEY",
        json_schema_extra={"env": "AUTHJWT_SECRET_KEY"},
    )
    authjwt_access_token_expires: int = Field(
        900, 
        alias="JWT_ACCESS_EXP_TIME", 
        json_schema_extra={"env": "JWT_ACCESS_EXP_TIME"}
    )  # 15 minutes
    authjwt_refresh_token_expires: int = Field(
        86400, 
        alias="JWT_REFRESH_EXP_TIME", 
        json_schema_extra={"env": "JWT_REFRESH_EXP_TIME"}
    )  # 24 hours
    
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
    
    
settings = Settings()

@AuthJWT.load_config
def get_config():
    return settings