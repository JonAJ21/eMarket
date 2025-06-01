from enum import Enum
from pydantic import BaseModel, UUID4

class Roles(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"

class RoleBase(BaseModel):
    id: UUID4
    name: str
    description: str | None = None

class RoleCreateDTO(BaseModel):
    name: str
    description: str | None = None

class RoleUpdateDTO(BaseModel):
    name: str
    description: str | None = None