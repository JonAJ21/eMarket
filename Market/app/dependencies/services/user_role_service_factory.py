from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from db.postgres import get_session
from db.redis import get_redis
from models.role import Role
from models.user import User
from repositories.role import CachedRolePostgreRepository, RolePostgreRepository
from repositories.user import CachedUserPostgreRepository, UserPostgreRepository
from services.user_role import UserRoleService
from services.cache import RedisCacheService
from services.uow import SQLAlchemyUnitOfWork

from dependencies.registrator import add_factory_to_mapper
from services.user_role import BaseUserRoleService

@add_factory_to_mapper(BaseUserRoleService)
@cache
def create_cached_user_role_service(
    session: AsyncSession = Depends(get_session), redis: Redis = Depends(get_redis)
) -> BaseUserRoleService:
    user_cache_service = RedisCacheService(client=redis, model=User)
    cached_user_repository = CachedUserPostgreRepository(
        session=session,
        cache_service=user_cache_service
    )
    role_cache_service = RedisCacheService(client=redis, _model=Role)
    cached_role_repository = CachedRolePostgreRepository(
        session=session,
        cache_service=role_cache_service
    )
    unit_of_work = SQLAlchemyUnitOfWork(session=session)
    return UserRoleService(
        user_repository=cached_user_repository,
        role_repository=cached_role_repository,
        uow=unit_of_work,
    ) 
    
@cache
def create_user_role_service(
    session: AsyncSession = Depends(get_session)
) -> BaseUserRoleService:
    user_repository = UserPostgreRepository(session=session)
    role_repository = RolePostgreRepository(session=session)
    unit_of_work = SQLAlchemyUnitOfWork(session=session)
    return UserRoleService(
        user_repository=user_repository,
        role_repository=role_repository,
        uow=unit_of_work,
    )