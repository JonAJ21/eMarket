from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 