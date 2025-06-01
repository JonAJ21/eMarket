from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, List

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
    attempted_at: datetime
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
    

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    role_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

class UserUpdateDTO(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class UserHistoryResponse(BaseModel):
    user_agent: Optional[str]
    user_device_type: Optional[str]
    attempted_at: datetime
    is_success: bool

    class Config:
        orm_mode = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
