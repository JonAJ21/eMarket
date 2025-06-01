from enum import Enum
from datetime import datetime

from pydantic import BaseModel, EmailStr

class SocialProvider(str, Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'
    
class SocialUserDTO(BaseModel):
    id: str
    login: str
    social_name: SocialProvider
    email: EmailStr | None = None

class SocialCreateDTO(BaseModel):
    user_id: str
    social_id: str
    social_name: SocialProvider
    created_at: datetime