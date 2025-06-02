import asyncio
from utils.data_service import DataService
from utils.clickhouse_client import ClickHouseClient
from utils.consumer import KafkaConsumer
from utils.config import settings


class App:
    def __init__(self):
        self.kafka_config = {
            "bootstrap_servers": settings.kafka_url,
            "topic": settings.kafka_topic,
            "group_id": settings.kafka_group_id
        }
        
        self.clickhouse_config = {
            "host": settings.clickhouse_db_host,
            "port": settings.clickhouse_db_port,
            "database": settings.clickhouse_db_name,
            "user": settings.clickhouse_user_name,
            "password": settings.clickhouse_user_password
        }
    
    async def run(self):
        while(True):
            try:
                kafka_consumer = KafkaConsumer(**self.kafka_config)
                clickhouse_client = ClickHouseClient(**self.clickhouse_config)
                data_service = DataService(clickhouse_client)
                
                await kafka_consumer.start()
                
                async for message in kafka_consumer.consume_messages():
                    await data_service.process_event(message) 
            except Exception as e:
                await asyncio.sleep(1)
                print(f"Application error: {e}")
            finally:
                await kafka_consumer.stop()
                
if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
