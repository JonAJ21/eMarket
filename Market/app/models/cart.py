from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from bson import ObjectId
from .product import PyObjectId

class CartItem(BaseModel):
    product_id: PyObjectId
    quantity: int = Field(gt=0)

class Cart(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True 