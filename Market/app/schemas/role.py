from pydantic import BaseModel

class RoleCreateDTO(BaseModel):
    name: str
    description: str | None = None