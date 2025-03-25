from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.role import RoleCreateDTO
from repositories.postgre import PostgreRepository
from models.role import Role
from repositories.base import BaseRepository


class BaseRoleRepository(BaseRepository, ABC):
    @abstractmethod
    async def get_role_by_name(self, *, name: str) -> Role | None:
        ...
        
class RolePostgreRepository(PostgreRepository[Role, RoleCreateDTO], BaseRoleRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Role)
        
    async def get_role_by_name(self, *, name) -> Role | None:
        statement = select(self._model).where(self._model.name == name)
        results = await self._session.execute(statement)
        return results.scalar_one_or_none()