from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    ) 