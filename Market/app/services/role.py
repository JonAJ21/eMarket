from abc import ABC, abstractmethod
from typing import Any

from repositories.role import BaseRoleRepository
from services.uow import BaseUnitOfWork
from models.role import Role
from schemas.result import Error, GenericResult, Result
from schemas.role import RoleCreateDTO, RoleUpdateDTO


class BaseRoleService(ABC):
    @abstractmethod
    async def get_roles(self, *, skip: int = 0, limit: int = 100) -> GenericResult[list[Role]]:
        ...
        
    @abstractmethod
    async def get_role(self, *, role_id: Any) -> GenericResult[Role]:
        ...
        
    @abstractmethod
    async def create_role(self, dto: RoleCreateDTO ) -> GenericResult[Role]:
        ...
        
    @abstractmethod
    async def update_role(self, role_id: Any, dto: RoleCreateDTO) -> GenericResult[Role]:
        ...
    
    @abstractmethod
    async def delete_role(self, role_id: Any) -> Result:
        ...
        

class RoleService(BaseRoleService):
    def __init__(self, repository: BaseRoleRepository, uow: BaseUnitOfWork):
        self._repository = repository
        self._uow = uow
        
    async def get_roles(self, *, skip: int = 0, limit: int = 100) -> GenericResult[list[Role]]:
        roles = await self._repository.gets(skip=skip, limit=limit)
        return GenericResult.success(value=roles)
    
    async def get_role(self, *, role_id: Any) -> GenericResult[Role]:
        role = await self._repository.get(role_id=role_id)
        if not role:
            return GenericResult.failure(
                error=Error(
                    message='Role not found', code='role_not_found',
                )
            )
        return GenericResult.success(value=role)
    
    async def create_role(self, dto: RoleCreateDTO) -> GenericResult[Role]:
        role = await self._repository.get_role_by_name(name=dto.name)
        if not role:
            role = await self._repository.insert(data=dto)
            await self._uow.commit()
            return GenericResult.success(value=role)
        return GenericResult.failure(
            error=Error(
                message='Role already exists', code='role_already_exists',
            )
        )
        
    async def update_role(self, dto: RoleUpdateDTO) -> GenericResult[Role]:
        role = await self._repository.get(role_id=dto.role_id)
        if not role:
            return GenericResult.failure(
                error=Error(
                    message='Role not found', code='role_not_found',
                )
            )
        role.update_role(**dto.model_dump())
        await self._uow.commit()
        return GenericResult.success(value=role)
    
    async def delete_role(self, role_id: Any) -> Result:
        role = await self._repository.get(role_id=role_id)
        if not role:
            return Result.failure(
                error=Error(
                    message='Role not found', code='role_not_found',
                )
            )
        await self._repository.delete(role_id=role_id)
        await self._uow.commit()
        return Result.success()
        