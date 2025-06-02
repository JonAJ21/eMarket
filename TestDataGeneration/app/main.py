import json
from kafka import KafkaProducer
import psycopg2
from pymongo import MongoClient
from utils.config import settings
from utils.generate import DataGenerator

pg_conn = psycopg2.connect(
    dbname=settings.postgres_db_name,
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_db_host,
    port=settings.postgres_db_port
)
pg_cursor = pg_conn.cursor()

mongo_client = MongoClient("mongodb://mongodb_database:27017/")
mongo_db = mongo_client[settings.mongo_db_name]



kafka_producer = KafkaProducer(
    bootstrap_servers=[settings.kafka_url],
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
)

def main():
    dataGenerator = DataGenerator(
        pg_cursor=pg_cursor,
        pg_conn=pg_conn,
        mongo_client=mongo_client,
        mongo_db=mongo_db,
        kafka_producer=kafka_producer
    )
    
    print("Generating data...")
    
    print("Generating roles...")
    dataGenerator.generate_roles()
    
    print("Generating users...")
    user_ids = dataGenerator.generate_users(25)
    
    pg_cursor.execute("SELECT user_id FROM sellers_info")
    seller_ids = [row[0] for row in pg_cursor.fetchall()]
    
    print("Generating categories...")
    category_ids = dataGenerator.generate_categories()
    
    print("Generating products...")
    product_ids = dataGenerator.generate_products(category_ids, seller_ids, 60)
    
    print("Generating carts...")
    dataGenerator.generate_carts(user_ids, product_ids)

    print("Generating reviews...")
    dataGenerator.generate_reviews(user_ids, product_ids, 120)
    
    print("Generating Kafka events...")
    dataGenerator.generate_kafka_events(user_ids, 30)
    
    print("Data generation complete!")
    
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()
    kafka_producer.flush()
    kafka_producer.close()


if __name__ == "__main__":
    main()
