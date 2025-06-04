from pydantic import Field
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
    
    clickhouse_url: str = Field(
        "",
        alias="CLICKHOUSE_URL",
        json_schema_extra={"env": "CLICKHOUSE_URL"}
    )
    
    clickhouse_db_name: str = Field(
        "",
        alias="CLICKHOUSE_DB_NAME",
        json_schema_extra={"env": "CLICKHOUSE_DB_NAME"}
    )
    
    clickhouse_db_host: str = Field(
        "",
        alias="CLICKHOUSE_DB_HOST",
        json_schema_extra={"env": "CLICKHOUSE_DB_HOST"}
    )
    
    clickhouse_db_port: int = Field(
        "",
        alias="CLICKHOUSE_DB_PORT",
        json_schema_extra={"env": "CLICKHOUSE_DB_PORT"}
    )
    
    clickhouse_user_name: str = Field(
        "",
        alias="CLICKHOUSE_USER_NAME",
        json_schema_extra={"env": "CLICKHOUSE_USER_NAME"}
    )
    
    clickhouse_user_password: str = Field(
        "",
        alias="CLICKHOUSE_USER_PASSWORD",
        json_schema_extra={"env": "CLICKHOUSE_USER_PASSWORD"}
    )
    
    
settings = Settings()