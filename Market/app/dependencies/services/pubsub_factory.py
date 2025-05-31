from functools import cache

from fastapi import Depends
from redis.asyncio import Redis


from db.redis import get_redis
from services.pubsub import BasePubSub, RedisPubSub
from dependencies.registrator import add_factory_to_mapper


@add_factory_to_mapper(BasePubSub)
@cache
def create_pubsub_service(
    redis: Redis = Depends(get_redis)
) -> BasePubSub:
    return RedisPubSub(
        client=redis
    )