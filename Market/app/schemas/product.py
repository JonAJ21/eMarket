from typing import List, Optional
from pydantic import BaseModel, Field, confloat, conint, ConfigDict
from datetime import datetime
from bson import ObjectId

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    price: confloat(gt=0)
    category_id: str  # Будем хранить как строку, а конвертировать в ObjectId при необходимости
    stock: conint(ge=0)
    images: List[str] = []

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[confloat(gt=0)] = None
    category_id: Optional[str] = None
    stock: Optional[conint(ge=0)] = None
    images: Optional[List[str]] = None

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ProductInDB(ProductBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ProductResponse(ProductInDB):
    pass 