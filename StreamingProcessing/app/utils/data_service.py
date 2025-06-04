import logging
from typing import Any, Dict, List
from utils.scheamas import DimOrderRecord, FactSalesRecord, PaymentOrderEvent
from utils.clickhouse_client import ClickHouseClient

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, clickhouse_client: ClickHouseClient):
        self.clickhouse = clickhouse_client
    
    async def process_event(self, event_data: Dict[str, Any]):
        try:
            event = PaymentOrderEvent(**event_data)
            transformed = await self.transform(event)
            
            async with self.clickhouse as ch:
                await ch.insert_fact_sales(transformed["fact_sales"])
                await ch.insert_dim_orders(transformed["dim_orders"])
            
            logger.info(f"Processed event {event.id}")
            return True
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            return False
        
    async def transform(self, event: PaymentOrderEvent) -> Dict[str, List]:
        fact_sales = [
            FactSalesRecord(
                id=str(event.id),
                order_id=str(event.order_id),
                user_id=str(event.user_id),
                seller_id=str(product.seller_id),
                product_id=str(product.product_id),
                is_paid=1 if event.is_paid else 0,
                amount=float(product.amount),
                currency=event.currency,
                created_at=event.created_at.strftime("%Y-%m-%d %H:%M:%S")
            )
            for product in event.products
        ]
        
        dim_order = DimOrderRecord(
            id=str(event.order_id),
            order_status=event.order_status,
            delivery_address=event.delivery_address,
            delivery_method=event.delivery_method,
            created_at=event.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return {
            "fact_sales": fact_sales,
            "dim_orders": [dim_order]
        }