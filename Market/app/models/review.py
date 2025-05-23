from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, conint, ConfigDict
from bson import ObjectId

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    product_id: str
    user_id: str
    rating: conint(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 