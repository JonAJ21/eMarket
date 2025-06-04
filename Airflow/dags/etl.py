from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from clickhouse_driver import Client
from airflow.models import Variable
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    MINIO_BUCKET = 'batch-processing'
    MINIO_PREFIX = 'staging/'
    MINIO_ACCESS_KEY = Variable.get("minio_access_key")
    MINIO_SECRET_KEY = Variable.get("minio_secret_key")
    CH_HOST = Variable.get("ch_host")
    CH_PORT = Variable.get("ch_port")
    CH_USER = Variable.get("ch_user")
    CH_PASSWORD = Variable.get("ch_password")
    CH_DATABASE = Variable.get("ch_database")
    BATCH_SIZE = 50000
    MONGO_DB = Variable.get("mongo_db")
    
    MIN_ROWS_VALIDATION = {
        'dim_users': 0,
        'dim_roles': 0,
        'dim_sellers': 0,
        'dim_social_accounts': 0,
        'dim_products': 0,
        'dim_categories': 0,
        'dim_reviews': 0
    }

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

dag = DAG(
    'etl_from_postgre_and_mongo_to_clickhouse',
    default_args=default_args,
    description='ETL from postgre and mongo to clickhouse',
    schedule='@daily',
    tags=['data_warehouse', 'etl', 'snowflake'],
    max_active_runs=1,
)

def get_ch_client() -> Client:
    return Client(
        host=Config.CH_HOST,
        port=Config.CH_PORT,
        user=Config.CH_USER,
        password=Config.CH_PASSWORD,
        database=Config.CH_DATABASE
    )

def upload_df_to_minio(df: pd.DataFrame, object_name: str) -> None:
    try:
        s3_hook = S3Hook(aws_conn_id='s3-minio')
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        full_key = f"{Config.MINIO_PREFIX}{object_name}"
        s3_hook.load_bytes(
            bytes_data=buffer.getvalue(),
            key=full_key,
            bucket_name=Config.MINIO_BUCKET,
            replace=True
        )
        logger.info(f"Data successfully loaded into MinIO: {full_key}")
    except Exception as e:
        logger.error(f"Loading error in MinIO: {str(e)}")
        raise

def load_from_minio_to_ch(object_name: str, table_name: str) -> None:
    try:
        ch_client = get_ch_client()
        full_key = f"{Config.MINIO_PREFIX}{object_name}"
        
        query = f"""
        INSERT INTO {Config.CH_DATABASE}.{table_name}
        SELECT * FROM s3(
            'http://minio:9000/{Config.MINIO_BUCKET}/{full_key}',
            '{Config.MINIO_ACCESS_KEY}',
            '{Config.MINIO_SECRET_KEY}',
            'Parquet'
        )
        """
        ch_client.execute(query)
        logger.info(f"Data successfully loaded into {table_name} from {full_key}")
    except Exception as e:
        logger.error(f"Loading error in ClickHouse: {str(e)}")
        raise

def cleanup_minio_staging() -> None:
    try:
        s3_hook = S3Hook(aws_conn_id='s3-minio')
        files = s3_hook.list_keys(
            bucket_name=Config.MINIO_BUCKET,
            prefix=Config.MINIO_PREFIX
        )
        
        if files:
            s3_hook.delete_objects(
                bucket=Config.MINIO_BUCKET,
                keys=files
            )
            logger.info(f"Cleared {len(files)} files from MinIO")
        else:
            logger.info("There are no files in MinIO")
    except Exception as e:
        logger.error(f"Clearing error MinIO: {str(e)}")
        raise

def check_source_available(source: str) -> bool:
    try:
        if source == 'postgres':
            hook = PostgresHook(conn_id='postgres_default')
            conn = hook.get_conn()
            conn.close()
        elif source == 'mongo':
            hook = MongoHook(conn_id='mongo_default')
            conn = hook.get_conn()
            conn.server_info()
        elif source == 'minio':
            hook = S3Hook(aws_conn_id='s3-minio')
            hook.check_for_bucket(bucket_name=Config.MINIO_BUCKET)
        else:
            raise ValueError(f"Unknown source: {source}")
        
        logger.info(f"Source {source} is available")
        return True
    except Exception as e:
        logger.error(f"Source {source} is not available: {str(e)}")
        raise

def etl_dim_users(**kwargs):
    try:
        pg_hook = PostgresHook(conn_id='postgres_default')
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_users"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = f"""
        SELECT id, login, first_name, last_name, fathers_name, phone, email, 
               is_active, created_at, updated_at
        FROM users
        WHERE updated_at > '{last_loaded}'
        ORDER BY id
        """
        
        df = pg_hook.get_pandas_df(query)
        
        if df.empty:
            logger.info("There are no new data for dim_users")
            return
        
        df['is_active'] = df['is_active'].astype(int)
        
        object_name = "dim_users.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_users')
        
        logger.info(f"Loaded {len(df)} rows in dim_users")
    except Exception as e:
        logger.error(f"Error ETL for dim_users: {str(e)}")
        raise

def etl_dim_roles(**kwargs):
    try:
        pg_hook = PostgresHook(conn_id='postgres_default')
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_roles"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = f"""
        SELECT r.id, ur.user_id, r.name, r.description, r.created_at, r.updated_at
        FROM roles r
        JOIN user_role ur ON r.id = ur.role_id
        WHERE r.updated_at > '{last_loaded}'
        ORDER BY r.id
        """
        
        df = pg_hook.get_pandas_df(query)
        
        if df.empty:
            logger.info("There are no new data for dim_roles")
            return
        
        object_name = "dim_roles.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_roles')
        
        logger.info(f"Loaded {len(df)} rows in dim_roles")
    except Exception as e:
        logger.error(f"Error ETL for dim_roles: {str(e)}")
        raise

def etl_dim_sellers(**kwargs):
    try:
        pg_hook = PostgresHook(conn_id='postgres_default')
        ch_client = get_ch_client()

        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_sellers"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = f"""
        SELECT u.id as id, s.name, s.address, s.postal_code, s.inn, s.kpp, 
               s.payment_account, s.correspondent_account, s.bank, s.bik, 
               s.is_verified, s.verificated_at, s.created_at, s.updated_at
        FROM sellers_info s
        JOIN users u ON s.user_id = u.id
        WHERE s.updated_at > '{last_loaded}'
        ORDER BY u.id
        """
        
        df = pg_hook.get_pandas_df(query)
        
        if df.empty:
            logger.info("There are no new data for dim_sellers")
            return
        
        df['is_verified'] = df['is_verified'].astype(int)
        
        object_name = "dim_sellers.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_sellers')
        
        logger.info(f"Loaded {len(df)} rows in dim_sellers")
    except Exception as e:
        logger.error(f"Error ETL for dim_sellers: {str(e)}")
        raise

def etl_dim_social_accounts(**kwargs):
    try:
        pg_hook = PostgresHook(conn_id='postgres_default')
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(created_at) FROM {Config.CH_DATABASE}.dim_social_accounts"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = f"""
        SELECT id, user_id, social_id, social_name::text, created_at
        FROM social_accounts
        WHERE created_at > '{last_loaded}'
        ORDER BY id
        """
        
        df = pg_hook.get_pandas_df(query)
        
        if df.empty:
            logger.info("There are no new data for dim_social_accounts")
            return
        
        object_name = "dim_social_accounts.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_social_accounts')
        
        logger.info(f"Loaded {len(df)} rows in dim_social_accounts")
    except Exception as e:
        logger.error(f"Error ETL for dim_social_accounts: {str(e)}")
        raise

def etl_dim_products(**kwargs):
    try:
        mongo_hook = MongoHook(mongo_conn_id='mongo_default')
        db = mongo_hook.get_conn().get_database(Config.MONGO_DB)
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_products"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = {'updated_at': {'$gt': last_loaded}}
        products = list(db['products'].find(query))
        
        if not products:
            logger.info("There are no new data for dim_products")
            return
        
        rows = []
        for product in products:
            row = {
                'id': product.get('id'),
                'name': product.get('name'),
                'description': product.get('description', ''),
                'price': float(product.get('price', 0)),
                'seller_id': product.get('seller_id'),
                'category_id': str(product.get('category_id', '')),
                'stock': int(product.get('stock', 0)),
                'images': product.get('images', []),
                'created_at': product.get('created_at'),
                'updated_at': product.get('updated_at')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        object_name = "dim_products.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_products')
        
        logger.info(f"Loaded {len(df)} rows in dim_products")
    except Exception as e:
        logger.error(f"Error ETL for dim_products: {str(e)}")
        raise

def etl_dim_categories(**kwargs):
    try:
        mongo_hook = MongoHook(mongo_conn_id='mongo_default')
        db = mongo_hook.get_conn().get_database(Config.MONGO_DB)
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_categories"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = {'updated_at': {'$gt': last_loaded}}
        categories = list(db['categories'].find(query))
        
        if not categories:
            logger.info("There are no new data for dim_categories")
            return
        
        rows = []
        for category in categories:
            row = {
                'id': category.get('id'),
                'name': category.get('name'),
                'description': category.get('description', ''),
                'parent_id': category.get('parent_id'),
                'created_at': category.get('created_at'),
                'updated_at': category.get('updated_at')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        object_name = "dim_categories.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_categories')
        
        logger.info(f"Loaded {len(df)} rows in dim_categories")
    except Exception as e:
        logger.error(f"Error ETL for dim_categories: {str(e)}")
        raise

def etl_dim_reviews(**kwargs):
    try:
        mongo_hook = MongoHook(mongo_conn_id='mongo_default')
        db = mongo_hook.get_conn().get_database(Config.MONGO_DB)
        ch_client = get_ch_client()
        
        last_loaded_query = f"SELECT max(updated_at) FROM {Config.CH_DATABASE}.dim_reviews"
        last_loaded = ch_client.execute(last_loaded_query)
        last_loaded = last_loaded[0][0] if last_loaded and last_loaded[0][0] else datetime(1970, 1, 1)
        
        query = {'updated_at': {'$gt': last_loaded}}
        reviews = list(db['reviews'].find(query))
        
        if not reviews:
            logger.info("There are no new data for dim_reviews")
            return
        
        rows = []
        for review in reviews:
            row = {
                'id': review.get('id'),
                'product_id': review.get('product_id'),
                'user_id': review.get('user_id'),
                'rating': int(review.get('rating', 0)),
                'comment': review.get('comment'),
                'created_at': review.get('created_at'),
                'updated_at': review.get('updated_at')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        object_name = "dim_reviews.parquet"
        upload_df_to_minio(df, object_name)
        load_from_minio_to_ch(object_name, 'dim_reviews')
        
        logger.info(f"Loaded {len(df)} rows in dim_reviews")
    except Exception as e:
        logger.error(f"Error ETL for dim_reviews: {str(e)}")
        raise

def validate_dim_users():
    validate_table('dim_users', Config.MIN_ROWS_VALIDATION['dim_users'])

def validate_dim_roles():
    validate_table('dim_roles', Config.MIN_ROWS_VALIDATION['dim_roles'])

def validate_dim_sellers():
    validate_table('dim_sellers', Config.MIN_ROWS_VALIDATION['dim_sellers'])

def validate_dim_social_accounts():
    validate_table('dim_social_accounts', Config.MIN_ROWS_VALIDATION['dim_social_accounts'])

def validate_dim_products():
    validate_table('dim_products', Config.MIN_ROWS_VALIDATION['dim_products'])

def validate_dim_categories():
    validate_table('dim_categories', Config.MIN_ROWS_VALIDATION['dim_categories'])

def validate_dim_reviews():
    validate_table('dim_reviews', Config.MIN_ROWS_VALIDATION['dim_reviews'])

def validate_table(table_name: str, min_rows: int) -> None:
    try:
        ch_client = get_ch_client()
        
        query = f"""
        SELECT count() 
        FROM {Config.CH_DATABASE}.{table_name} 
        WHERE toDate(updated_at) = today()
        """
        if table_name == "dim_social_accounts":
            query = f"""
            SELECT count() 
            FROM {Config.CH_DATABASE}.{table_name} 
            WHERE toDate(created_at) = today()
            """
        result = ch_client.execute(query)
        count = result[0][0] if result else 0
        
        if count < min_rows:
            error_msg = f"Validation failed {table_name}: loaded {count} strings (min {min_rows})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Validation sucessed {table_name}: loaded {count} strings")
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    
start_task = EmptyOperator(task_id='start', dag=dag)
end_task = EmptyOperator(task_id='end', dag=dag)

postgres_sensor = PythonOperator(
    task_id='check_postgres_available',
    python_callable=check_source_available,
    op_kwargs={'source': 'postgres'},
    dag=dag,
)

mongo_sensor = PythonOperator(
    task_id='check_mongo_available',
    python_callable=check_source_available,
    op_kwargs={'source': 'mongo'},
    dag=dag,
)

minio_sensor = PythonOperator(
    task_id='check_minio_available',
    python_callable=check_source_available,
    op_kwargs={'source': 'minio'},
    dag=dag,
)

etl_dim_users_task = PythonOperator(
    task_id='etl_dim_users',
    python_callable=etl_dim_users,
    dag=dag,
)

etl_dim_roles_task = PythonOperator(
    task_id='etl_dim_roles',
    python_callable=etl_dim_roles,
    dag=dag,
)

etl_dim_sellers_task = PythonOperator(
    task_id='etl_dim_sellers',
    python_callable=etl_dim_sellers,
    dag=dag,
)

etl_dim_social_accounts_task = PythonOperator(
    task_id='etl_dim_social_accounts',
    python_callable=etl_dim_social_accounts,
    dag=dag,
)

etl_dim_products_task = PythonOperator(
    task_id='etl_dim_products',
    python_callable=etl_dim_products,
    dag=dag,
)

etl_dim_categories_task = PythonOperator(
    task_id='etl_dim_categories',
    python_callable=etl_dim_categories,
    dag=dag,
)

etl_dim_reviews_task = PythonOperator(
    task_id='etl_dim_reviews',
    python_callable=etl_dim_reviews,
    dag=dag,
)

validate_dim_users_task = PythonOperator(
    task_id='validate_dim_users',
    python_callable=validate_dim_users,
    dag=dag,
)

validate_dim_roles_task = PythonOperator(
    task_id='validate_dim_roles',
    python_callable=validate_dim_roles,
    dag=dag,
)

validate_dim_sellers_task = PythonOperator(
    task_id='validate_dim_sellers',
    python_callable=validate_dim_sellers,
    dag=dag,
)

validate_dim_social_accounts_task = PythonOperator(
    task_id='validate_dim_social_accounts',
    python_callable=validate_dim_social_accounts,
    dag=dag,
)

validate_dim_products_task = PythonOperator(
    task_id='validate_dim_products',
    python_callable=validate_dim_products,
    dag=dag,
)

validate_dim_categories_task = PythonOperator(
    task_id='validate_dim_categories',
    python_callable=validate_dim_categories,
    dag=dag,
)

validate_dim_reviews_task = PythonOperator(
    task_id='validate_dim_reviews',
    python_callable=validate_dim_reviews,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_minio',
    python_callable=cleanup_minio_staging,
    trigger_rule='all_done',
    dag=dag,
)

start_task >> [postgres_sensor, mongo_sensor, minio_sensor]

postgres_sensor >> [etl_dim_users_task, etl_dim_roles_task, 
                   etl_dim_sellers_task, etl_dim_social_accounts_task]

mongo_sensor >> [etl_dim_products_task, etl_dim_categories_task, 
                etl_dim_reviews_task]


etl_dim_users_task >> validate_dim_users_task
etl_dim_roles_task >> validate_dim_roles_task
etl_dim_sellers_task >> validate_dim_sellers_task
etl_dim_social_accounts_task >> validate_dim_social_accounts_task
etl_dim_products_task >> validate_dim_products_task
etl_dim_categories_task >> validate_dim_categories_task
etl_dim_reviews_task >> validate_dim_reviews_task

[validate_dim_users_task, validate_dim_roles_task, 
 validate_dim_sellers_task, validate_dim_social_accounts_task,
 validate_dim_products_task, validate_dim_categories_task,
 validate_dim_reviews_task] >> cleanup_task

cleanup_task >> end_task