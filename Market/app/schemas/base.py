from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from uuid import UUID

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class CartItem(BaseModel):
    product_id: UUID
    seller_id: UUID
    amount: float

class BaseSchema(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            ObjectId: str,
            PyObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        populate_by_name = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
