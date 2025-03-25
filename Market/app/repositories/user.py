from abc import abstractmethod
from typing import Any, List

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.postgre import PostgreRepository
from schemas.user import UserCreateDTO, UserHistoryCreateDTO
from schemas.result import Error, GenericResult, ModelType
from repositories.base import BaseRepository
from schemas.social import SocialCreateDTO, SocialNetworks
from models.social_account import SocialAccount
from models.user import User
from models.user_history import UserHistory

class BaseUserRepository(BaseRepository):
    @abstractmethod
    async def get_by_login(self, *, login: str) -> User | None:
        ...
        
    @abstractmethod
    async def get_user_history(
        self, *, user_id: str, skip: int = 0, limit: int
    ) -> list[UserHistory]:
        ...
        
    @abstractmethod
    async def get_user_social(
        self, *, social_id: str, social_name: SocialNetworks
    ) -> SocialAccount:
        ...
        
    @abstractmethod
    async def insert_user_login(
        self, *, data: UserHistoryCreateDTO
    ) -> GenericResult[UserHistory]:
        ...
        
    @abstractmethod
    async def insert_user_social(
        self, *, data: SocialCreateDTO
    ) -> GenericResult[SocialAccount]:
        ...
        
class UserPostgreRepository(PostgreRepository[User, UserCreateDTO], BaseUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)
        
    async def get(self, *, id: Any) -> ModelType | None:
        statement = (
            select(self._model)
            .options(noload(self._model.history))
            .options(selectinload(self._model.roles))
            .where(self._model.id == id)
        )
        return (await self._session.execute(statement)).scalar_one_or_none()
        
    async def get_by_login(self, *, login: str) -> User | None:
        statement = select(self._model).where(self._model.login == login)
        return (await self._session.execute(statement)).scalar_one_or_none()
    
    async def get_user_history(
        self, *, user_id: Any, skip: int = 0, limit: int = 100
    ) -> List[UserHistory]:
        statement = (
            select(UserHistory)
            .where(UserHistory.user_id == user_id)
            .order_by()
            .offset(skip)
            .limit(limit)
        )
        return (await self._session.execute(statement)).scalars().all()
    
    async def get_user_social(
        self, *, social_id: str, social_name: SocialNetworks
    ) -> SocialAccount | None:
        statement = (
            select(SocialAccount)
            .where(
                and_(
                    SocialAccount.social_name == social_name,
                    SocialAccount.social_id == social_id
                )
            )
        )
        return (await self._session.execute(statement)).scalar_one_or_none()
    
    async def insert_user_login(
        self, *, user_id: Any, data: UserHistoryCreateDTO
    ) -> GenericResult[UserHistory]:
        user: User = await self.get(id=user_id)
        if not user:
            return GenericResult.failure(
                error=Error(error_code="USER_NOT_FOUND", reason="User not found"),
            )
        user_history = UserHistory(**data.model_dump())
        user.add_user_session(user_history)
        return GenericResult.success(user_history)
    
    async def insert_user_social(
        self, *, user_id: Any, data: SocialCreateDTO
    ) -> GenericResult[SocialAccount]:
        user: User = await self.get(id=user_id)
        if not user:
            return GenericResult.failure(
                error=Error(error_code="USER_NOT_FOUND", reason="User not found"),
            )
        social = SocialAccount(**data.model_dump())
        user.add_social_account(social)
        return GenericResult.success(social)
    
        
    