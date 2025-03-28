from abc import ABC, abstractmethod
from typing import Any

from repositories.user import BaseUserRepository
from services.uow import BaseUnitOfWork
from schemas.result import Error, Result

class BaseUserRoleService(ABC):
    @abstractmethod
    async def assign_role_to_user(self, user_id: Any, role_id: Any) -> Result:
        ...
        
    @abstractmethod
    async def remove_role_from_user(self, user_id: Any, role_id: Any) -> Result:
        ...
       

class  UserRoleService(BaseUserRoleService):
    def __init__(self, user_repository: BaseUserRepository, role_repository: BaseUserRepository, uow: BaseUnitOfWork):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._uow = uow
        
    async def assign_role_to_user(self, user_id: Any, role_id: Any) -> Result:
        user = await self._user_repository.get(id=user_id)
        role = await self._role_repository.get(id=role_id)
        if not user:
            return Result.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        if not role:
            return Result.failure(
                error=Error(
                    message='Role not found', code='role_not_found',
                )
            )
        user.assign_role(role)
        await self._uow.commit()
        return Result.success()
        
    async def remove_role_from_user(self, user_id: Any, role_id: Any) -> Result:
        user = await self._user_repository.get(id=user_id)
        role = await self._role_repository.get(id=role_id)
        if not user:
            return Result.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        if not role:
            return Result.failure(
                error=Error(
                    message='Role not found', code='role_not_found',
                )
            )
        user.remove_role(role)
        await self._uow.commit()
        return Result.success()