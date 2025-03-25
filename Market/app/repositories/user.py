from abc import ABC, abstractmethod
from dataclasses import dataclass

from schemas.social import SocialNetworks
from models.social_account import SocialAccount
from models.user import User
from models.user_history import UserHistory

@dataclass
class BaseUserRepository(ABC):
    @abstractmethod
    async def get_by_login(self, *, login: str) -> User:
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
        
    # @abstractmethod
    # async def insert_user_login(
    #     self, *, user_id: Any, data: UserHistoryCreateDTO
    # ) -> GenericResult[UserHistory]:
    #     ...
        
    # @abstractmethod
    # async def insert_user_social(
    #     self, *, user_id: Any, data: SocialCreateDTO
    # ) -> GenericResult[SocialAccount]:
    #     ...