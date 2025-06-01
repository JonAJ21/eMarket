from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    kafka_url: str = Field(
        "localhost:9092",
        alias="KAFKA_URL",
        json_schema_extra={"env": "KAFKA_URL"},
    )
    kafka_topic: str = Field(
        "telegram_bot",
        alias="KAFKA_TOPIC",
        json_schema_extra={"env": "KAFKA_TOPIC"}
    )
    kafka_group_id: str = Field(
        "telegram_bot",
        alias="KAFKA_GROUP_ID",
        json_schema_extra={"env": "KAFKA_GROUP_ID"}
    )
    
settings = Settings()