from abc import ABC, abstractmethod
from typing import Any

from models.role import Role
from models.user import User
from repositories.user import BaseUserRepository
from services.uow import BaseUnitOfWork

class BaseUserRoleService(ABC):
    @abstractmethod
    async def assign_role_to_user(self, user_id: Any, role_id: Any) -> None:
        ...
        
    @abstractmethod
    async def remove_role_from_user(self, user_id: Any, role_id: Any) -> None:
        ...
       

class  UserRoleService(BaseUserRoleService):
    def __init__(self, user_repository: BaseUserRepository, role_repository: BaseUserRepository, uow: BaseUnitOfWork):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._uow = uow
        
    async def assign_role_to_user(self, user_id: Any, role_id: Any) -> None:
        user: User = await self._user_repository.get(id=user_id)
        role: Role = await self._role_repository.get(id=role_id)
        if not user:
            raise RuntimeError('User not found')
        if not role:
            raise RuntimeError('Role not found')
        user.assign_role(role)
        await self._uow.commit()
        
    async def remove_role_from_user(self, user_id: Any, role_id: Any) -> None:
        user: User = await self._user_repository.get(id=user_id)
        role: Role = await self._role_repository.get(id=role_id)
        if not user:
            raise RuntimeError('User not found')
        if not role:
            raise RuntimeError('Role not found')
        user.remove_role(role)
        await self._uow.commit()