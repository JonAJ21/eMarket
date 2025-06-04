from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_url: str = Field(
        "kafka:29092",
        alias="KAFKA_URL",
        json_schema_extra={"env": "KAFKA_URL"},
    )
    kafka_topic: str = Field(
        "payment_orders",
        alias="KAFKA_TOPIC",
        json_schema_extra={"env": "KAFKA_TOPIC"}
    )
    kafka_group_id: str = Field(
        "sale_streaming",
        alias="KAFKA_GROUP_ID",
        json_schema_extra={"env": "KAFKA_GROUP_ID"}
    )
    
    postgres_connection: PostgresDsn = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        alias="POSTGRES_CONNECTION",
        json_schema_extra={"env": "POSTGRES_CONNECTION"},
    )
    
    postgres_db_name: str = Field(
        "",
        alias="POSTGRES_DB_NAME",
        json_schema_extra={"env": "POSTGRES_DB_NAME"}
    )
    
    postgres_user: str = Field(
        "",
        alias="POSTGRES_USER",
        json_schema_extra={"env": "POSTGRES_USER"}
    )
    
    postgres_password: str = Field(
        "",
        alias="POSTGRES_PASSWORD",
        json_schema_extra={"env": "POSTGRES_PASSWORD"}
    )
    
    postgres_db_port: int = Field(
        "",
        alias="POSTGRES_DB_PORT",
        json_schema_extra={"env": "POSTGRES_DB_PORT"}
    )
    
    postgres_db_host: str = Field(
        5432,
        alias="POSTGRES_DB_HOST",
        json_schema_extra={"env": "POSTGRES_DB_HOST"}
    )
    
    mongo_db_url: str = Field(
        "",
        alias="MONGODB_URL",
        json_schema_extra={"env": "MONGODB_URL"}
    )
    
    mongo_db_name: str = Field(
        "",
        alias="MONGODB_DB_NAME",
        json_schema_extra={"env": "MONGODB_DB_NAME"}
    )
    
    mongo_db_username: str = Field(
        "",
        alias="MONGODB_USERNAME",
        json_schema_extra={"env": "PMONGODB_USERNAME"}
    )
    
    mongo_db_password: str = Field(
        "",
        alias="MONGODB_PASSWORD",
        json_schema_extra={"env": "MONGODB_PASSWORD"}
    )
    
    mongo_db_host: str = Field(
        "",
        alias="MONGODB_HOST",
        json_schema_extra={"env": "MONGODB_HOST"}
    )
    
    mongo_db_port: int = Field(
        27017,
        alias="MONGODB_PORT",
        json_schema_extra={"env": "MONGODB_PORT"}
    )
    
    
    
    

settings = Settings()