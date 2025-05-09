from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, conint
from bson import ObjectId
from .product import PyObjectId

class Review(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    product_id: PyObjectId
    user_id: PyObjectId
    rating: conint(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True 