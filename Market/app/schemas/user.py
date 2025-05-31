from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, EmailStr

class UserDeviceType(str, Enum):
    web = 'WEB'


class UserBase(BaseModel):
    id: UUID
    login: str

class UserCreateDTO(BaseModel):
    login: str
    password: str
    
class UserHistoryCreateDTO(BaseModel):
    user_id: UUID
    user_agent: str
    user_device_type: UserDeviceType
    # attempted_at: datetime
    is_success: bool
    
class UserUpdatePasswordDTO(BaseModel):
    user_id: UUID
    old_password: str
    new_password: str
    

class UserUpdatePersonalDTO(BaseModel):
    user_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    fathers_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    
