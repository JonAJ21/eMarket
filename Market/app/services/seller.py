from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from models.seller_info import SellerInfo
from schemas.seller import SellerCreateDTO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseSellerService(ABC):
    @abstractmethod
    async def create_store(self, user_id: UUID, dto: SellerCreateDTO) -> SellerInfo: ...
    @abstractmethod
    async def update_store(self, user_id: UUID, dto: SellerCreateDTO) -> SellerInfo: ...
    @abstractmethod
    async def delete_store(self, user_id: UUID) -> None: ...
    @abstractmethod
    async def get_store_by_user(self, user_id: UUID) -> Optional[SellerInfo]: ...
    @abstractmethod
    async def list_verified_stores(self, skip: int, limit: int) -> List[SellerInfo]: ...
    @abstractmethod
    async def get_store_by_id(self, market_id: UUID) -> Optional[SellerInfo]: ...
    @abstractmethod
    async def list_unverified_stores(self, skip: int, limit: int) -> List[SellerInfo]: ...
    @abstractmethod
    async def verify_store(self, market_id: UUID) -> None: ...

class SellerService(BaseSellerService):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_store(self, user_id: UUID, dto: SellerCreateDTO) -> SellerInfo:
        existing = await self.get_store_by_user(user_id)
        if existing:
            raise ValueError("Store for this user already exists")
        seller = SellerInfo(user_id=user_id, **dto.dict())
        self._session.add(seller)
        await self._session.commit()
        await self._session.refresh(seller)
        return seller

    async def update_store(self, user_id: UUID, dto: SellerCreateDTO) -> SellerInfo:
        seller = await self.get_store_by_user(user_id)
        if not seller:
            raise ValueError("Store not found")
        for field, value in dto.dict().items():
            setattr(seller, field, value)
        await self._session.commit()
        await self._session.refresh(seller)
        return seller

    async def delete_store(self, user_id: UUID) -> None:
        seller = await self.get_store_by_user(user_id)
        if not seller:
            raise ValueError("Store not found")
        await self._session.delete(seller)
        await self._session.commit()

    async def get_store_by_user(self, user_id: UUID) -> Optional[SellerInfo]:
        stmt = select(SellerInfo).where(SellerInfo.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_verified_stores(self, skip: int, limit: int) -> List[SellerInfo]:
        stmt = select(SellerInfo).where(SellerInfo.is_verified == True).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_store_by_id(self, market_id: UUID) -> Optional[SellerInfo]:
        stmt = select(SellerInfo).where(SellerInfo.user_id == market_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_unverified_stores(self, skip: int, limit: int) -> List[SellerInfo]:
        stmt = select(SellerInfo).where(SellerInfo.is_verified == False).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def verify_store(self, market_id: UUID) -> None:
        seller = await self.get_store_by_id(market_id)
        if not seller:
            raise ValueError("Store not found")
        seller.is_verified = True
        await self._session.commit() 