from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 