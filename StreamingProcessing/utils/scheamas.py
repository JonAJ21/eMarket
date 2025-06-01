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
    
