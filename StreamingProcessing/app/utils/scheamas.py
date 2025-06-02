from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class CartItem(BaseModel):
	product_id: UUID
	seller_id: UUID
	amount: float

class PaymentOrderEvent(BaseModel):
    id: UUID
    user_id: UUID
    order_id: UUID
    order_status: str
    products: List[CartItem]
    is_paid: bool
    currency: str = "RUB"
    delivery_address: str
    delivery_method: str
    created_at: datetime
    
class FactSalesRecord(BaseModel):
    id: str
    order_id: str
    user_id: str
    seller_id: str
    product_id: str
    is_paid: int
    amount: float
    currency: str
    created_at: datetime
    
class DimOrderRecord(BaseModel):
    id: str
    order_status: str
    delivery_address: str
    delivery_method: str
    created_at: datetime
