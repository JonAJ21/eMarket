from enum import Enum
from pydantic import BaseModel

class Roles(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"

class RoleCreateDTO(BaseModel):
    name: str
    description: str | None = None
    
class RoleUpdateDTO(BaseModel):
    role_id: str
    name: str
    description: str | None = None