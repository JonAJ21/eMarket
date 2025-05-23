from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from bson import ObjectId

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[str] = None  # Храним как строку, конвертируем в ObjectId при необходимости

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[str] = None

class CategoryInDB(CategoryBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class CategoryResponse(CategoryInDB):
    pass

class CategoryWithSubcategories(CategoryResponse):
    subcategories: list['CategoryResponse'] = [] 