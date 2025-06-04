from abc import ABC, abstractmethod
from typing import Any

from repositories.role import BaseRoleRepository
from services.uow import BaseUnitOfWork
from models.role import Role
from schemas.result import Error, GenericResult, Result
from schemas.role import RoleCreateDTO, RoleUpdateDTO


class BaseRoleService(ABC):
    @abstractmethod
    async def get_roles(self, *, skip: int = 0, limit: int = 100) -> list[Role]:
        ...
        
    @abstractmethod
    async def get_role(self, *, role_id: Any) -> Role:
        ...
        
    @abstractmethod
    async def create_role(self, *, dto: RoleCreateDTO ) -> Role:
        ...
        
    @abstractmethod
    async def update_role(self, *, dto: RoleUpdateDTO) -> Role:
        ...
    
    @abstractmethod
    async def delete_role(self, *, role_id: Any) -> None:
        ...
        

class RoleService(BaseRoleService):
    def __init__(self, repository: BaseRoleRepository, uow: BaseUnitOfWork):
        self._repository = repository
        self._uow = uow
        
    async def get_roles(self, *, skip: int = 0, limit: int = 100) -> list[Role]:
        roles = await self._repository.gets(skip=skip, limit=limit)
        return roles
    
    async def get_role(self, *, role_id: Any) -> Role:
        role = await self._repository.get(id=role_id)
        if not role:
            raise RuntimeError('Role not found')
        return role
    
    async def create_role(self, dto: RoleCreateDTO) -> Role:
        role = await self._repository.get_role_by_name(name=dto.name)
        if role:
            RuntimeError('Role already exists')
        role = await self._repository.insert(data=dto)
        await self._uow.commit()
        return role
        
    async def update_role(self, dto: RoleUpdateDTO) -> Role:
        role: Role = await self._repository.get(id=dto.role_id)
        if not role:
            raise RuntimeError('Role not found')
        role.update_role(**dto.model_dump())
        await self._uow.commit()
        return role
    
    async def delete_role(self, role_id: Any) -> None:
        role = await self._repository.get(id=role_id)
        if not role:
            raise RuntimeError('Role not found')
        await self._repository.delete(id=role_id)
        await self._uow.commit()
        