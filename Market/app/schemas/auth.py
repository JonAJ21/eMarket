from pydantic import BaseModel


class UserLoginDTO(BaseModel):
    login: str
    password: str
    user_agent: str
    