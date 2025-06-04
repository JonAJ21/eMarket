from functools import cache

from fastapi import Depends
from redis.asyncio.client import Redis

from db.redis import get_redis
from storages.token import BaseTokenStorage
from storages.token import RedisTokenStorage
from dependencies.registrator import add_factory_to_mapper
from storages.token import BaseTokenStorage


@add_factory_to_mapper(BaseTokenStorage)
@cache
def create_token_storage(redis_client: Redis = Depends(get_redis)) -> BaseTokenStorage:
    return RedisTokenStorage(client=redis_client)