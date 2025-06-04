from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, conint, ConfigDict
from uuid import uuid4

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    product_id: str
    user_id: str
    rating: conint(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 