from enum import Enum
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import Field, BaseModel

from .base import BaseSchema, CartItem

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"

class DeliveryMethod(str, Enum):
    PICKUP = "pickup"
    COURIER = "courier"
    POST = "post"

class DeliveryAddress(BaseSchema):
    city: str
    street: str
    house: str
    apartment: Optional[str] = None
    postal_code: str

    def __str__(self) -> str:
        return f"{self.city}, {self.street}, {self.house}" + (f", кв. {self.apartment}" if self.apartment else "")

class Order(BaseSchema):
    user_id: UUID
    items: List[CartItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    payment_id: Optional[str] = None
    delivery_address: DeliveryAddress
    delivery_method: DeliveryMethod
    payment_url: Optional[str] = None

class OrderCreate(BaseModel):
    user_id: UUID
    delivery_address: DeliveryAddress
    delivery_method: DeliveryMethod

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_id: Optional[str] = None
    payment_url: Optional[str] = None

class SalesEvent(BaseSchema):
    id: UUID
    order_id: UUID
    user_id: UUID
    seller_id: UUID
    product_id: UUID
    is_paid: bool
    amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderEvent(BaseSchema):
    id: UUID
    code_status: str
    delivery_address: str
    delivery_method: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentOrderEvent(BaseSchema):
    id: UUID
    user_id: UUID
    order_id: UUID
    order_status: str
    products: List[CartItem]
    is_paid: bool
    currency: str = "RUB"
    delivery_address: str
    delivery_method: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_sales_events(self) -> List[SalesEvent]:
        return [
            SalesEvent(
                id=uuid4(),
                order_id=self.order_id,
                user_id=self.user_id,
                seller_id=product.seller_id,
                product_id=product.product_id,
                is_paid=self.is_paid,
                amount=product.amount,
                created_at=self.created_at
            )
            for product in self.products
        ]

    def to_order_event(self) -> OrderEvent:
        return OrderEvent(
            id=self.order_id,
            code_status=self.order_status,
            delivery_address=self.delivery_address,
            delivery_method=self.delivery_method,
            created_at=self.created_at
        )
