from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from db.postgres import get_session
from db.redis import get_redis
from dependencies.registrator import add_factory_to_mapper
from models.role import Role
from repositories.role import CachedRolePostgreRepository
from services.cache import RedisCacheService
from services.role import BaseRoleService, RoleService
from services.uow import SQLAlchemyUnitOfWork


@add_factory_to_mapper(BaseRoleService)
@cache
def create_role_service(
    session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
) -> BaseRoleService:
    cache_service = RedisCacheService(client=redis, model=Role)
    cached_repository = CachedRolePostgreRepository(
        session=session,
        cache_service=cache_service
    )
    unit_of_work = SQLAlchemyUnitOfWork(_session=session)
    return RoleService(repository=cached_repository, uow=unit_of_work)
    