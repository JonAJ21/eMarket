import json
from abc import ABC, abstractmethod
from typing import Type

from redis.asyncio import Redis

from schemas.result import ModelType


class BaseCacheService(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs) -> str:
        ...
        
    @abstractmethod
    async def set(self, *args, **kwargs):
        ...
        
    @abstractmethod
    async def delete(self, *args, **kwargs):
        ...
        
        
class RedisCacheService(BaseCacheService):
    def __init__(self, client: Redis, model: Type[ModelType]):
        self._client = client
        self._model = model
        
    async def get(self, *, key: str) -> ModelType | None:
        document = await self._client.get(key)
        if not document:
            return None
        return self._model(**json.loads(document))
    
    async def set(self, *, key: str, value: ModelType):
        await self._client.set(key, json.dumps(value.model_dump()))
        
    async def delete(self, *, key: str):
        if await self._client.exists(key):
            await self._client.delete(key)