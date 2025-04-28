from datetime import datetime, UTC
from uuid import uuid4
from pydantic import BaseModel



class TokenData(BaseModel):
    sub: str
    jti: str = str(uuid4())
    iat: datetime = datetime.now(UTC)
    exp: datetime | None = None

class Token(BaseModel):
    access_token: str | None
    refresh_token: str | None
    
class TokenJTI(BaseModel):
    access_token_jti: str | None
    refresh_token_jti: str | None
    
class TokenValidation(BaseModel):
    access_token: str