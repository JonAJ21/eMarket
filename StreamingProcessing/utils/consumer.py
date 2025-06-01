from typing import Callable
from aiokafka import AIOKafkaConsumer
from config import settings
import json



def get_consumer():
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_url,
        group_id=settings.kafka_group_id,
        auto_offset_reset='earliest'
    )
    
class KafkaConsumer:
    def __init__(self, topic, group_id):
        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=settings.kafka_url,
            group_id=group_id,
            auto_offset_reset='earliest'
        )
        
    async def start(self, callback: Callable):
        await self._consumer.start()
        try:
            async for msg in self._consumer:
                try:
                    message = 
                