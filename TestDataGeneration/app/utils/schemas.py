from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

# Enums for PostgreSQL

class SocialProviderEnum(str, Enum):
    GOOGLE = 'GOOGLE'
    YANDEX = 'YANDEX'
    
class UserDeviceTypeEnum(str, Enum):
    web = 'web'

# MongoDB models
class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float
    
class Product(BaseModel):
    id: str
    seller_id: str
    name: str
    description: str
    price: float
    category_id: str
    stock: int
    images: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class Category(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class Cart(BaseModel):
    id: str
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class Review(BaseModel):
    id: str
    product_id: str
    user_id: str
    rating: Annotated[int, Field(ge=1, le=5)]
    comment: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Kafka models
class CartItemKafka(BaseModel):
    product_id: str
    seller_id: str
    amount: float

class PaymentOrderEvent(BaseModel):
    id: str
    user_id: str
    order_id: str
    order_status: str
    products: List[CartItemKafka]
    is_paid: bool
    currency: str = "RUB"
    delivery_address: str
    delivery_method: str
    created_at: datetime

