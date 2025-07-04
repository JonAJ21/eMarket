from abc import ABC, abstractmethod
from typing import Any, List

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession

from models.seller_info import SellerInfo
from schemas.seller import SellerCreateDTO
from services.cache import BaseCacheService
from repositories.postgre import CachedPostgreRepository, PostgreRepository
from schemas.user import UserCreateDTO, UserHistoryCreateDTO
from repositories.base import BaseRepository
from schemas.social import SocialCreateDTO, SocialProvider
from models.social_account import SocialAccount
from models.user import User
from models.user_history import UserHistory

class BaseUserRepository(BaseRepository, ABC):
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
        self, *, social_id: str, social_name: SocialProvider
    ) -> SocialAccount | None:
        ...
    
    @abstractmethod
    async def get_seller_info(
        self, *, user_id: str
    ) -> SellerInfo | None:
        ...
    
    @abstractmethod
    async def insert_user_login(
        self, *, dto: UserHistoryCreateDTO
    ) -> UserHistory | None:
        ...
        
    @abstractmethod
    async def insert_user_social(
        self, *, dto: SocialCreateDTO
    ) -> SocialAccount | None:
        ...
        
    @abstractmethod
    async def insert_seller_info(
        self, *, dto: SellerCreateDTO,  
    ) -> SellerInfo:
        ...
        
class UserPostgreRepository(
    PostgreRepository[User, UserCreateDTO],
    BaseUserRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)
        
    async def get(self, *, id: Any) -> User | None:
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
        self, *, social_id: str, social_name: SocialProvider
    ) -> SocialAccount | None:
        statement = (
            select(SocialAccount)
            .where(
                and_(
                    SocialAccount.social_id == social_id,
                    SocialAccount.social_name == social_name
                )
            )
        )
        return (await self._session.execute(statement)).scalar_one_or_none()
    
    async def get_seller_info(
        self, *, user_id: str
    ) -> SellerInfo | None:
        statement = (
            select(SellerInfo)
            .where(SellerInfo.user_id == user_id)
        )
        return (await self._session.execute(statement)).scalar_one_or_none()
    
    async def insert_user_login(
        self, *, data: UserHistoryCreateDTO
    ) -> UserHistory | None:
        user: User = await self.get(id=data.user_id)
        if not user:
            return None
        user_history = UserHistory(**data.model_dump())
        user.add_user_session(user_history)
        return user_history
    
    async def insert_user_social(
        self, *, data: SocialCreateDTO
    ) -> SocialAccount | None:
        user: User = await self.get(id=data.user_id)
        if not user:
            return None
        social = SocialAccount(**data.model_dump())
        user.add_social_account(social)
        return social
    
    async def insert_seller_info(
        self, *, dto: SellerCreateDTO
    ) -> SellerInfo | None:
        user: User = await self.get(id=dto.user_id)
        if not user:
            return None
        seller_info = SellerInfo(**dto.model_dump())
        user.add_seller_info(seller_info)
        return seller_info
    
class CachedUserPostgreRepository(
    CachedPostgreRepository[User, UserCreateDTO],
    UserPostgreRepository
):
    def __init__(
        self, session: AsyncSession,  cache_service: BaseCacheService
    ):  
        super().__init__(session=session, model=User, cache_service=cache_service)
        
    async def get_by_login(self, *, login: str) -> User | None:
        key = f"{self._model.__name__}_{login}"
        if self._cache_service is not None:
            entity = await self._cache_service.get(key=key)
        if not entity:
            entity = await super().get_by_login(login=login)
        return entity
    
    async def get_user_history(
        self, *, user_id: Any, skip: int = 0, limit: int = 100
    ) -> List[UserHistory]:
        return await super().get_user_history(
            user_id=user_id, skip=skip, limit=limit
        )
        
    async def get_user_social(
        self, *, social_id: str, social_name: SocialProvider
    ) -> SocialAccount | None:
        return await super().get_user_social(
            social_id=social_id, social_name=social_name
        )
    
    async def get_seller_info(
        self, *, user_id: str
    ) -> SellerInfo | None:
        return await super().get_seller_info(user_id=user_id)
    
    async def insert_user_login(
        self, *, data: UserHistoryCreateDTO
    ) -> UserHistory | None:
        return await super().insert_user_login(data=data)
        
    async def insert_user_social(
        self, *, data: SocialCreateDTO
    ) -> SocialAccount | None:
        return await super().insert_user_social(data=data)
    
    async def insert_seller_info(
        self, *, dto: SellerCreateDTO
    ) -> SellerInfo | None:
        return await super().insert_seller_info(dto=dto)