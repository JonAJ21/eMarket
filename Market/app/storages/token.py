from abc import ABC, abstractmethod

from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from schemas.token import TokenJTI
from core.config import settings

class BaseTokenStorage(ABC):
    @abstractmethod
    async def store_token(self, *args, **kwargs):
        ...
    
    @abstractmethod
    async def get_token(self, *args, **kwargs):
        ...
        
    @abstractmethod
    async def check_expiration(self, *args, **kwargs) -> bool:
        ...
        

class RedisTokenStorage(BaseTokenStorage):
    def __init__(self, *, client: Redis):
        self._client = client
        
    async def store_token(self, *, token_jti: TokenJTI) -> None:
        async def _store_token(pipeline: Pipeline):
            if token_jti.refresh_token_jti:
                await pipeline.setex(
                    name=token_jti.refresh_token_jti,
                    time=settings.authjwt_refresh_token_expires,
                    value=str(True)
                )
            if token_jti.access_token_jti:
                await pipeline.setex(
                    name=token_jti.access_token_jti,
                    time=settings.authjwt_access_token_expires,
                    value=str(True)
                )
            
        await self._client.transaction(_store_token)
  
    async def get_token(self, *, key: str) -> str | None:
        return await self._client.get(key)
    
    async def check_expiration(self, *, jti: str) -> bool:
        return (await self.get_token(key=jti)) == "True"