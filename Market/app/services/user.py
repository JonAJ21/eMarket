from abc import ABC, abstractmethod
from typing import Any

from repositories.user import BaseUserRepository
from services.uow import BaseUnitOfWork
from models.user import User
from models.user_history import UserHistory
from schemas.result import GenericResult, Result
from schemas.social import SocialUser
from schemas.user import UserCreateDTO, UserHistoryCreateDTO, UserUpdateEmailDTO, UserUpdatePasswordDTO


class BaseUserService(ABC):
    @abstractmethod
    async def get_user_history(
        self, *, user_id: Any, skip: int, limit: int
    ) -> GenericResult[list[UserHistory]]:
        ...

    @abstractmethod
    async def get_users(self, *, skip: int, limit: int) -> GenericResult[list[User]]:
        ...

    @abstractmethod
    async def update_password(
        self, *, dto: UserUpdatePasswordDTO
    ) -> GenericResult[User]:
        ...

    @abstractmethod
    async def create_user(self, dto: UserCreateDTO) -> GenericResult[User]:
        ...

    @abstractmethod
    async def insert_user_login(
        self, *, dto: UserHistoryCreateDTO
    ) -> Result:
        ...

    @abstractmethod
    async def get_user(self, *, user_id: Any) -> GenericResult[User]:
        ...

    @abstractmethod
    async def get_user_by_login(self, *, login: str) -> GenericResult[User]:
        ...

    @abstractmethod
    async def get_or_create_user(self, *, social: SocialUser) -> GenericResult[User]:
        ...

    @abstractmethod
    async def update_user_email(
        self, dto: UserUpdateEmailDTO
    ) -> GenericResult[User]:
        ...

    @abstractmethod
    async def delete_user(self, *, user_id: Any) -> Result:
        ...
        

class UserService(BaseUserService):
    def __init__(self, repository: BaseUserRepository, uow: BaseUnitOfWork):
        self._repository = repository
        self._uow = uow
        
    async def get_user_history(self, *, user_id, skip, limit) -> GenericResult[list[UserHistory]]:
        ...
        
    async def get_users(self, *, skip, limit):
        return await super().get_users(skip=skip, limit=limit)
    
    async def update_password(self, *, dto: UserUpdatePasswordDTO):
        return await super().update_password(dto=dto)
    
    async def create_user(self, dto: UserCreateDTO):
        return await super().create_user(dto=dto)
    
    async def insert_user_login(self, *, dto):
        return await super().insert_user_login(dto=dto)
    
    async def get_user(self, *, user_id):
        return await super().get_user(user_id=user_id)
    
    async def get_user_by_login(self, *, login):
        return await super().get_user_by_login(login=login)
    
    async def get_or_create_user(self, *, social):
        return await super().get_or_create_user(social=social)
    
    async def update_user_email(self, dto):
        return await super().update_user_email(dto)
    
    async def delete_user(self, *, user_id):
        return await super().delete_user(user_id=user_id)