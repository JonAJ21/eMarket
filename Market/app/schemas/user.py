from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, EmailStr

class UserDeviceType(str, Enum):
    web = 'WEB'


class UserBase(BaseModel):
    id: UUID
    login: str
    email: EmailStr | None

class UserCreateDTO(BaseModel):
    login: str
    password: str
    email: EmailStr | None = None
    
class UserHistoryCreateDTO(BaseModel):
    user_id: UUID
    user_agent: str
    user_device_type: str
    success: bool
    attempted: datetime
    
class UserUpdatePasswordDTO(BaseModel):
    user_id: UUID
    old_password: str
    new_password: str
    
class UserUpdateEmailDTO(BaseModel):
    user_id: UUID
    email: EmailStr | None
    
