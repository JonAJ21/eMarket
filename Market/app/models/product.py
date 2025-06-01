from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    seller_id: str
    name: str
    description: str
    price: float
    category_id: str
    stock: int
    images: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 