from abc import ABC, abstractmethod
from typing import Any

from faker import Faker

from models.social_account import SocialAccount
from repositories.user import BaseUserRepository
from services.uow import BaseUnitOfWork
from models.user import User
from models.user_history import UserHistory
from schemas.result import GenericResult, Result, Error
from schemas.social import SocialUser
from schemas.user import UserCreateDTO, UserHistoryCreateDTO, UserUpdateEmailDTO, UserUpdatePasswordDTO


class BaseUserService(ABC):
    @abstractmethod
    async def get_user_history(
        self, *, user_id: Any, skip: int = 0, limit: int = 100
    ) -> GenericResult[list[UserHistory]]:
        ...

    @abstractmethod
    async def get_users(self, *, skip: int = 0, limit: int= 100) -> GenericResult[list[User]]:
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
        
    async def get_user_history(self, *, user_id: Any, skip: int = 0, limit: int = 100) -> GenericResult[list[UserHistory]]:
        user_history = await self._repository.get_user_history(
            user_id=user_id, skip=skip, limit=limit
        )
        return GenericResult.success(value=user_history)
        
    async def get_users(self, *, skip: int = 0, limit: int = 100) -> GenericResult[list[User]]:
        users = await self._repository.gets(skip=skip, limit=limit)
        return GenericResult.success(value=users)
    
    async def update_password(self, *, dto: UserUpdatePasswordDTO):
        user: User = await self._repository.get(id=dto.user_id)
        if user is None:
            return GenericResult.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        
        status = user.change_password(dto.old_password, dto.new_password)
        if not status:
            return GenericResult.failure(
                error=Error(
                    message='Incorrect password', code='incorrect_password',
                )
            )
        
        await self._uow.commit()
        
        return GenericResult.success(value=user)
        
    async def create_user(self, dto: UserCreateDTO) -> GenericResult[User]:
        user = await self._repository.get_by_login(login=dto.login)
        if user is not None:
            return GenericResult.failure(
                error=Error(
                    message='User already exists', code='user_already_exists',
                )
            )
        
        user = await self._repository.insert(data=dto)
        await self._uow.commit()
        return GenericResult.success(value=user)
        
    async def insert_user_login(self, *, dto: UserHistoryCreateDTO) -> Result:
        result = await self._repository.insert_user_login(data=dto)
        if result is None:
            return Result.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        await self._uow.commit()
        return Result.success()
    
    async def get_user(self, *, user_id: Any) -> GenericResult[User]:
        user = await self._repository.get(id=user_id)
        if not user:
            return GenericResult.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        return GenericResult.success(value=user)
    
    async def get_user_by_login(self, *, login: str) -> GenericResult[User]:
        user = await self._repository.get_by_login(login=login)
        if user is None:
            return GenericResult.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        return GenericResult.success(value=user)
    
    async def get_or_create_user(self, *, social: SocialUser) -> GenericResult[User]:
        social_user = await self._repository.get_user_social(
            social_id=social.id, social_name=social.social_name
        )
        if social_user is None:
            auto_password = Faker().password()
            user = await self.get_user_by_login(login=social.login)
            if user:
                return GenericResult.failure(
                    error=Error(
                        message='User already exists', code='user_already_exists',
                    )
                )
            
            user_dto = UserCreateDTO(
                login=social.login,
                password=auto_password,
                email=social.email
            )
            user: User= await self._repository.insert(data=user_dto)
            user.add_social_account(
                social_account=SocialAccount(
                    user_id=user.id,
                    social_id=social.id,
                    social_name=social.social_name
                )
            )
            await self._uow.commit()
            return GenericResult.success(value=user)
        
        user = await self.get_user(user_id=social_user.user_id)
        return GenericResult.success(value=user)
    
    async def update_user_email(self, dto: UserUpdateEmailDTO) -> GenericResult[User]:
        user: User = await self._repository.get(id=dto.user_id)
        if user is None:
            return GenericResult.failure(
                error=Error(
                    message='User not found', code='user_not_found',
                )
            )
        user.update_email(email=dto.email)
        await self._uow.commit()
        return GenericResult.success(value=user)
    
    async def delete_user(self, *, user_id: Any) -> Result:
        await self._repository.delete(id=user_id)
        await self._uow.commit()
        return Result.success()