from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Market.app.services.cache import BaseCacheService
from schemas.role import RoleCreateDTO
from repositories.postgre import CachedPostgreRepository, PostgreRepository
from models.role import Role
from repositories.base import BaseRepository


class BaseRoleRepository(BaseRepository, ABC):
    @abstractmethod
    async def get_role_by_name(self, *, name: str) -> Role | None:
        ...
        
class RolePostgreRepository(PostgreRepository[Role, RoleCreateDTO], BaseRoleRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Role)
        
    async def get_role_by_name(self, *, name: str) -> Role | None:
        statement = select(self._model).where(self._model.name == name)
        results = await self._session.execute(statement)
        return results.scalar_one_or_none()
    

 
class CachedRolePostgreRepository(
    CachedPostgreRepository[Role, RoleCreateDTO],
    RolePostgreRepository
):
    def __init__(self, session: AsyncSession, cache_service: BaseCacheService):
        super().__init__(session=session, model=Role, cache_service=cache_service)
        
    async def get_role_by_name(self, *, name: str) -> Role | None:
        key = f"{self._model.__name__}_{name}"
        if self._cache_service is not None:
            entity = await self._cache_service.get(key=key)
        if not entity:
            entity = await super().get_role_by_name(name=name)
        return entity
        
    