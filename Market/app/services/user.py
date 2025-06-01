from abc import ABC, abstractmethod
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from faker import Faker
from bcrypt import hashpw, gensalt

from models.social_account import SocialAccount
from repositories.user import BaseUserRepository
from services.uow import BaseUnitOfWork
from models.user import User
from models.user_history import UserHistory
from schemas.result import GenericResult, Result, Error
from schemas.social import SocialUserDTO
from schemas.user import UserCreateDTO, UserHistoryCreateDTO, UserUpdatePasswordDTO, UserUpdatePersonalDTO, UserUpdateDTO, UserResponse, UserHistoryResponse, UserListResponse


class BaseUserService(ABC):
    @abstractmethod
    async def get_user_history(
        self, *, user_id: Any, skip: int = 0, limit: int = 100
    ) -> list[UserHistory]:
        ...

    @abstractmethod
    async def get_users(self, *, skip: int = 0, limit: int= 100) -> list[User]:
        ...

    @abstractmethod
    async def update_password(self, *, dto: UserUpdatePasswordDTO) -> User:
        ...

    @abstractmethod
    async def create_user(self, *, dto: UserCreateDTO) -> GenericResult[User]:
        ...

    @abstractmethod
    async def insert_user_login(self, *, dto: UserHistoryCreateDTO) -> UserHistory:
        ...

    @abstractmethod
    async def get_user(self, *, user_id: Any) -> User:
        ...

    @abstractmethod
    async def get_user_by_login(self, *, login: str) -> User:
        ...

    @abstractmethod
    async def get_or_create_user(self, *, dto: SocialUserDTO) -> User:
        ...

    @abstractmethod
    async def update_personal(self, dto: UserUpdatePersonalDTO) -> User:
        ...

    @abstractmethod
    async def delete_user(self, *, user_id: Any) -> None:
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]: ...

    @abstractmethod
    async def list_users(self, skip: int, limit: int) -> UserListResponse: ...

    @abstractmethod
    async def update_user(self, user_id: UUID, dto: UserUpdateDTO) -> UserResponse: ...

    @abstractmethod
    async def assign_role(self, user_id: UUID, role_id: UUID) -> None: ...

    @abstractmethod
    async def get_user_history(self, user_id: UUID) -> List[UserHistoryResponse]: ...


class UserService(BaseUserService):
    def __init__(self, repository: BaseUserRepository, uow: BaseUnitOfWork, session: AsyncSession):
        self._repository = repository
        self._uow = uow
        self._session = session
        
    async def get_user_history(
        self, *, user_id: Any, skip: int = 0, limit: int = 100
    ) -> list[UserHistory]:
        user_history = await self._repository.get_user_history(
            user_id=user_id, skip=skip, limit=limit
        )
        return user_history
        
    async def get_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        users = await self._repository.gets(skip=skip, limit=limit)
        return users
    
    async def update_password(self, *, dto: UserUpdatePasswordDTO) -> User:
        user: User = await self._repository.get(id=dto.user_id)
        if not user:
            raise RuntimeError('User not found')
        
        user.change_password(dto.old_password, dto.new_password)

        await self._uow.commit()
        return user
        
    async def create_user(self, dto: UserCreateDTO) -> GenericResult[User]:
        user = await self._repository.get_by_login(login=dto.login)
        if user:
            return GenericResult.failure(Error(message="User already exists", code="user_exists"))
        user = await self._repository.insert(data=dto)
        await self._uow.commit()
        return GenericResult.success(user)
        
    async def insert_user_login(self, *, dto: UserHistoryCreateDTO) -> UserHistory:
        user_history = await self._repository.insert_user_login(data=dto)
        if not user_history:
            raise RuntimeError('User not found')
        await self._uow.commit()
        return user_history
    
    async def get_user(self, *, user_id: Any) -> User:
        user = await self._repository.get(id=user_id)
        if not user:
            raise RuntimeError('User not found')
        return user
    
    async def get_user_by_login(self, *, login: str) -> User:
        user = await self._repository.get_by_login(login=login)
        if not user:
            raise RuntimeError('User not found')
        return user
    
    async def get_or_create_user(self, *, social: SocialUserDTO) -> User:
        social_user = await self._repository.get_user_social(
            social_id=social.id, social_name=social.social_name
        )
        if not social_user:
            auto_password = Faker().password()
            user = await self.get_user_by_login(login=social.login)
            if user:
                raise RuntimeError('User already exists')
            
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
            return user
        
        user = await self.get_user(user_id=social_user.user_id)
        return user
    
    async def update_personal(self, dto: UserUpdatePersonalDTO) -> User:
        user: User = await self._repository.get(id=dto.user_id)
        if not user:
            raise RuntimeError('User not found')
        
        user.update_personal(first_name=dto.first_name,
                             last_name=dto.last_name,
                             fathers_name=dto.fathers_name,
                             phone=dto.phone,
                             email=dto.email)
        
        await self._uow.commit()
        return user
    
    async def delete_user(self, *, user_id: Any) -> None:
        await self._repository.delete(id=user_id)
        await self._uow.commit()

    async def get_user_by_id(self, user_id: UUID) -> Optional[UserResponse]:
        user = await self._repository.get(id=user_id)
        if not user:
            return None

        full_name = ' '.join(filter(None, [user.first_name, user.last_name, user.fathers_name])) or None

        role_id = user.roles[0].id if user.roles else None
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=full_name,
            is_active=user.is_active,
            role_id=role_id,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def list_users(self, skip: int, limit: int) -> UserListResponse:

        users = await self._repository.gets(skip=skip, limit=limit)
        total = len(users) 
        user_responses = []
        for user in users:
            full_name = ' '.join(filter(None, [user.first_name, user.last_name, user.fathers_name])) or None
            role_id = user.roles[0].id if user.roles else None
            user_responses.append(UserResponse(
                id=user.id,
                email=user.email,
                full_name=full_name,
                is_active=user.is_active,
                role_id=role_id,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))
        return UserListResponse(users=user_responses, total=total)

    async def update_user(self, user_id: UUID, dto: UserUpdateDTO) -> UserResponse:
        user = await self._repository.get(id=user_id)
        if not user:
            raise ValueError("User not found")
        if dto.full_name:

            parts = dto.full_name.split()
            user.first_name = parts[0] if len(parts) > 0 else None
            user.last_name = parts[1] if len(parts) > 1 else None
            user.fathers_name = parts[2] if len(parts) > 2 else None
        if dto.email:
            user.email = dto.email
        if dto.password:
            user.password = hashpw(dto.password.encode(), gensalt()).decode()
        await self._uow.commit()
        full_name = ' '.join(filter(None, [user.first_name, user.last_name, user.fathers_name])) or None
        role_id = user.roles[0].id if user.roles else None
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=full_name,
            is_active=user.is_active,
            role_id=role_id,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def assign_role(self, user_id: UUID, role_id: UUID) -> None:

        user = await self._repository.get(id=user_id)
        if not user:
            raise ValueError("User not found")
        from models.role import Role
        from sqlalchemy import select
        result = await self._session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError("Role not found")
        user.assign_role(role)
        await self._uow.commit()

    async def get_user_history(self, user_id: UUID) -> List[UserHistoryResponse]:
        history = await self._repository.get_user_history(user_id=user_id)
        responses = []
        for h in history:
            responses.append(UserHistoryResponse(
                action="login",  # Or whatever action is appropriate
                timestamp=getattr(h, 'attemted_at', None),
                details=h.user_agent
            ))
        return responses
        