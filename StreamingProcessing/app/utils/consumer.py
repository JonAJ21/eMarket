import logging
from typing import Any, AsyncGenerator
from aiokafka import AIOKafkaConsumer
import json

logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    
    async def start(self):
        await self.consumer.start()
        logger.info("Kafka consumer started")
    
    async def stop(self):
        await self.consumer.stop()
        logger.info("Kafka consumer stopped")
    
    async def consume_messages(self) -> AsyncGenerator[Any, None]:
        try:
            async for msg in self.consumer:
                yield msg.value
        except Exception as e:
            logger.error(f"Error consuming messages: {e}", exc_info=True)
            raise