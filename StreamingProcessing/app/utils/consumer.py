from typing import Any, AsyncGenerator
from aiokafka import AIOKafkaConsumer
import json

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
    
    async def stop(self):
        await self.consumer.stop()
    
    async def consume_messages(self) -> AsyncGenerator[Any, None]:
        try:
            async for msg in self.consumer:
                yield msg.value
        except Exception as e:
            print(f"Error consuming messages: {e}")
            raise