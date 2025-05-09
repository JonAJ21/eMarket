from typing import List, Optional
from pydantic import BaseModel, Field, conint
from datetime import datetime
from bson import ObjectId
from .product import PyObjectId

class CartItemBase(BaseModel):
    product_id: PyObjectId
    quantity: conint(gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: conint(gt=0)

class CartItemInDB(CartItemBase):
    pass

class CartBase(BaseModel):
    user_id: PyObjectId
    items: List[CartItemInDB] = []

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    items: List[CartItemInDB]

class CartInDB(CartBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

class CartResponse(CartInDB):
    pass

class CartItemResponse(CartItemInDB):
    product_name: str
    product_price: float
    total_price: float 