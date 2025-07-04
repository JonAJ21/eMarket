from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from db.postgres import get_session

from db.redis import get_redis
from dependencies.registrator import add_factory_to_mapper
from models.user import User
from repositories.user import CachedUserPostgreRepository
from services.cache import RedisCacheService
from services.uow import SQLAlchemyUnitOfWork
from services.user import BaseUserService, UserService


@add_factory_to_mapper(BaseUserService)
@cache
def create_user_service(
    session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
) -> BaseUserService:
    cache_service = RedisCacheService(client=redis, model=User)
    unit_of_work = SQLAlchemyUnitOfWork(session=session)
    cached_repository = CachedUserPostgreRepository(
        session=session,
        cache_service=cache_service,    
    )
    return UserService(repository=cached_repository, uow=unit_of_work, session=session)

def get_user_service(session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)) -> BaseUserService:
    from models.user import User
    from repositories.user import CachedUserPostgreRepository
    from services.cache import RedisCacheService
    from services.uow import SQLAlchemyUnitOfWork
    cache_service = RedisCacheService(client=redis, model=User)
    cached_repository = CachedUserPostgreRepository(session=session, cache_service=cache_service)
    unit_of_work = SQLAlchemyUnitOfWork(session=session)
    return UserService(repository=cached_repository, uow=unit_of_work, session=session)