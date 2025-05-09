from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from .product import PyObjectId

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[PyObjectId] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[PyObjectId] = None

class CategoryInDB(CategoryBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True

class CategoryResponse(CategoryInDB):
    pass

class CategoryWithSubcategories(CategoryResponse):
    subcategories: list['CategoryResponse'] = [] 