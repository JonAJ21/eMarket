
from typing import List

from aiochclient import ChClient
from aiohttp import ClientSession

from utils.scheamas import DimOrderRecord, FactSalesRecord


class ClickHouseClient:
    def __init__(self, host: str, port: int, database: str, user: str = "default", password: str = "", secure: bool = False):
        self.url = f"http{'s' if secure else ''}://{host}:{port}"
        self.database = database
        self.user = user
        self.password = password
    
    async def __aenter__(self):
        self.session = ClientSession()
        self.client = ChClient(
            self.session,
            url=self.url,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self
    
    async def __aexit__(self):
        await self.session.close()
    
    async def insert_fact_sales(self, records: List[FactSalesRecord]):
        if not records:
            return
        
        await self.client.execute(
            """
            INSERT INTO data_warehouse.fact_sales (
                id, order_id, user_id, seller_id, product_id, 
                is_paid, amount, currency, created_at
            ) VALUES
            """,
            *[(r.model_dump().values()) for r in records]
        )
    
    async def insert_dim_orders(self, records: List[DimOrderRecord]):
        if not records:
            return
        
        await self.client.execute(
            """
            INSERT INTO data_warehouse.dim_orders (
                id, order_status, delivery_address, delivery_method, created_at
            ) VALUES
            """,
            *[(r.model_dump().values()) for r in records]
        )