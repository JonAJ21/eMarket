import json
from kafka import KafkaProducer
import psycopg2
from pymongo import MongoClient


# pg_conn = psycopg2.connect(
#     dbname="your_dbname",
#     user="your_user",
#     password="your_password",
#     host="your_host"
# )
# pg_cursor = pg_conn.cursor()

# mongo_client = MongoClient("mongodb://localhost:27017/")
# mongo_db = mongo_client["ecommerce"]

# kafka_producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
# )

def main():
    print("Hello from testdatageneration!")
    e = input()
    print("Hello from testdatageneration!")


if __name__ == "__main__":
    main()
