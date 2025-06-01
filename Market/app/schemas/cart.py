from typing import List, Optional
from pydantic import BaseModel, Field, conint, ConfigDict
from datetime import datetime
from uuid import uuid4

class CartItemBase(BaseModel):
    product_id: str
    quantity: conint(gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[conint(gt=0)] = None

class CartItemInDB(CartItemBase):
    pass

class CartItemResponse(CartItemInDB):
    product_name: str
    product_price: float
    total_price: float

class CartBase(BaseModel):
    user_id: str
    items: List[CartItemInDB] = []

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    items: Optional[List[CartItemInDB]] = None

class CartInDB(CartBase):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class CartResponse(CartInDB):
    pass