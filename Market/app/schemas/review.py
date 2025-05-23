from typing import Optional
from pydantic import BaseModel, Field, conint, ConfigDict
from datetime import datetime
from bson import ObjectId

class ReviewBase(BaseModel):
    product_id: str
    user_id: str
    rating: conint(ge=1, le=5)
    comment: str = Field(..., min_length=1, max_length=1000)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = Field(None, min_length=1, max_length=1000)

class ReviewInDB(ReviewBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ReviewResponse(ReviewInDB):
    pass

class ProductRating(BaseModel):
    rating: float
    total_reviews: int 