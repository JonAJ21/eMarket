from pydantic import BaseModel

class RoleCreateDTO(BaseModel):
    name: str
    description: str | None = None
    
class RoleUpdateDTO(BaseModel):
    role_id: str
    name: str
    description: str | None = None