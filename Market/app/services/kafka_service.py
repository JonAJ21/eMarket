from aiokafka import AIOKafkaProducer
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self):
        self.producer: AIOKafkaProducer = None

    async def connect(self):
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            await self.producer.start()
            logger.info("Kafka producer started")

    async def disconnect(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
            self.producer = None

    async def send_event(self, topic: str, event_data: dict):
        await self.connect()
        try:
            await self.producer.send_and_wait(topic=topic, value=event_data)
            logger.info(f"Sent event to topic '{topic}'")
        except Exception as e:
            logger.exception(f"Error sending event to Kafka topic {topic}")
            raise

    async def send_sales_event(self, event_data: dict):
        await self.send_event(settings.KAFKA_SALES_TOPIC, event_data)

    async def send_order_event(self, event_data: dict):
        await self.send_event(settings.KAFKA_ORDERS_TOPIC, event_data)

kafka_service = KafkaService()
