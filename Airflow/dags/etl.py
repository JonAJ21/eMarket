from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mongo.hooks.mongo import MongoHook
from clickhouse_driver import Client as ClickHouseClient
from typing import Dict, List, Tuple
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

def get_clickhouse_client():
    return ClickHouseClient(
        host='clickhouse',
        port=9000,
        user='custom_user',
        password='',
        database='data_warehouse',
        settings={'use_numpy': True, 'async_insert': 1, 'wait_for_async_insert': 0}
    )

@task
def extract_postgres_data() -> Dict[str, List[Tuple]]:
    pg_hook = PostgresHook(postgres_conn_id='postgres')
    conn = pg_hook.get_conn()
    
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, login, first_name, last_name, fathers_name, 
                   phone, email, is_active, created_at, updated_at 
            FROM users
            WHERE updated_at >= %s
        """, [datetime.now() - timedelta(days=1)])
        users = cursor.fetchall()
        
        cursor.execute("""
            SELECT r.id, ur.user_id, r.name, r.description, r.created_at, r.updated_at
            FROM roles r
            JOIN user_role ur ON r.id = ur.role_id
            WHERE r.updated_at >= %s OR ur.user_id IN (
                SELECT id FROM users WHERE updated_at >= %s
            )
        """, [datetime.now() - timedelta(days=1)] * 2)
        roles = cursor.fetchall()
        
        cursor.execute("""
            SELECT user_id, name, address, postal_code, inn, kpp, 
                   payment_account, correspondent_account, bank, bik, 
                   is_verified, verificated_at, created_at, updated_at
            FROM sellers_info
            WHERE updated_at >= %s
        """, [datetime.now() - timedelta(days=1)])
        sellers = cursor.fetchall()
        
        cursor.execute("""
            SELECT id, user_id, social_id, social_name, created_at
            FROM social_accounts
            WHERE created_at >= %s
        """, [datetime.now() - timedelta(days=1)])
        social_accounts = cursor.fetchall()
    
    return {
        'users': users,
        'roles': roles,
        'sellers': sellers,
        'social_accounts': social_accounts
    }

@task
def extract_mongo_data() -> Dict[str, List[Dict]]:
    mongo_hook = MongoHook(conn_id='mongo')
    client = mongo_hook.get_conn()
    db = client.get_database('products_database')
    
    yesterday = datetime.now() - timedelta(days=1)
    
    products = list(db.products.find({
        'updated_at': {'$gte': yesterday}
    }, {
        '_id': 0,
        'id': 1,
        'name': 1,
        'description': 1,
        'price': 1,
        'category_id': 1,
        'stock': 1,
        'images': 1,
        'created_at': 1,
        'updated_at': 1
    }))
    
    categories = list(db.categories.find({
        'updated_at': {'$gte': yesterday}
    }, {
        '_id': 0,
        'id': 1,
        'name': 1,
        'description': 1,
        'parent_id': 1,
        'created_at': 1,
        'updated_at': 1
    }))
    
    reviews = list(db.reviews.find({
        'updated_at': {'$gte': yesterday}
    }, {
        '_id': 0,
        'id': 1,
        'product_id': 1,
        'user_id': 1,
        'rating': 1,
        'comment': 1,
        'created_at': 1,
        'updated_at': 1
    }))
    
    client.close()
    
    return {
        'products': products,
        'categories': categories,
        'reviews': reviews
    }

@task
def transform_postgres_data(pg_data: Dict[str, List[Tuple]]) -> Dict[str, List[Tuple]]:
    transformed_users = [
        (*row[:7], 1 if row[7] else 0, *row[8:])
        for row in pg_data['users']
    ]
    
    transformed_sellers = [
        (*row[:10], 1 if row[10] else 0, *row[11:])
        for row in pg_data['sellers']
    ]
    
    return {
        'users': transformed_users,
        'roles': pg_data['roles'],
        'sellers': transformed_sellers,
        'social_accounts': pg_data['social_accounts']
    }

@task
def transform_mongo_data(mongo_data: Dict[str, List[Dict]]) -> Dict[str, List[Tuple]]:
    transformed_products = [
        (
            p['id'], p['name'], p.get('description', ''),
            float(p['price']), p['category_id'], int(p['stock']),
            p.get('images', []), p['created_at'], p['updated_at']
        )
        for p in mongo_data['products']
    ]
    
    transformed_categories = [
        (
            c['id'], c['name'], c.get('description', ''),
            c.get('parent_id'), c['created_at'], c['updated_at']
        )
        for c in mongo_data['categories']
    ]
    
    transformed_reviews = [
        (
            r['id'], r['product_id'], r['user_id'],
            int(r['rating']), r['comment'],
            r['created_at'], r['updated_at']
        )
        for r in mongo_data['reviews']
    ]
    
    return {
        'products': transformed_products,
        'categories': transformed_categories,
        'reviews': transformed_reviews
    }

@task
def load_to_clickhouse(pg_data: Dict[str, List[Tuple]], mongo_data: Dict[str, List[Tuple]]):
    ch_client = get_clickhouse_client()
    
    try:
        if pg_data['users']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_users VALUES",
                pg_data['users'],
                types_check=True
            )
        
        if pg_data['roles']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_roles VALUES",
                pg_data['roles'],
                types_check=True
            )
        
        if pg_data['sellers']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_sellers VALUES",
                pg_data['sellers'],
                types_check=True
            )
        
        if pg_data['social_accounts']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_social_accounts VALUES",
                pg_data['social_accounts'],
                types_check=True
            )
        

        if mongo_data['products']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_products VALUES",
                mongo_data['products'],
                types_check=True
            )
        
        if mongo_data['categories']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_categories VALUES",
                mongo_data['categories'],
                types_check=True
            )
        
        if mongo_data['reviews']:
            ch_client.execute(
                "INSERT INTO data_warehouse.dim_reviews VALUES",
                mongo_data['reviews'],
                types_check=True
            )
    except Exception as e:
        logging.error(f"Error loading data to ClickHouse: {str(e)}")
        raise
    finally:
        ch_client.disconnect()

with DAG(
    'postgres_mongo_to_clickhouse',
    default_args=default_args,
    description='ETL from Postgres and MongoDB to ClickHouse',
    schedule='@daily',
    max_active_runs=1,
    tags=['data_warehouse'],
) as dag:
    
    pg_data = extract_postgres_data()
    mongo_data = extract_mongo_data()
    
    transformed_pg = transform_postgres_data(pg_data)
    transformed_mongo = transform_mongo_data(mongo_data)
    
    load_task = load_to_clickhouse(transformed_pg, transformed_mongo)
    
    pg_data >> transformed_pg
    mongo_data >> transformed_mongo
    [transformed_pg, transformed_mongo] >> load_task