from datetime import datetime

from pydantic import BaseModel, EmailStr

class UserCreateDTO(BaseModel):
    login: str
    password: str
    email: EmailStr | None = None
    
class UserHistoryCreateDTO(BaseModel):
    user_id: str
    user_agent: str
    user_device_type: str
    success: bool
    attempted: datetime = datetime.now()
    
class UserUpdatePasswordDTO(BaseModel):
    user_id: str
    old_password: str
    new_password: str
    
class UserUpdateEmailDTO(BaseModel):
    user_id: str
    email: EmailStr | None
    
