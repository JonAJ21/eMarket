from uuid import UUID
from typing import List
from repositories.seller import SellerInfoRepository
from services.uow import BaseUnitOfWork
from models.seller_info import SellerInfo
from schemas.seller import SellerInfoCreateDTO, SellerInfoUpdateDTO

class SellerInfoService:
    def __init__(self, repository: SellerInfoRepository, uow: BaseUnitOfWork):
        self._repository = repository
        self._uow = uow

    async def create_market(self, seller_id: UUID, dto: SellerInfoCreateDTO) -> SellerInfo:
        market = await self._repository.get_by_seller_id(seller_id=seller_id)
        if market:
            raise RuntimeError("Market already exists for this seller")
        market = SellerInfo(user_id=seller_id, **dto.model_dump())
        self._repository._session.add(market)
        await self._uow.commit()
        return market

    async def update_market(self, seller_id: UUID, dto: SellerInfoUpdateDTO) -> SellerInfo:
        market = await self._repository.get_by_seller_id(seller_id=seller_id)
        if not market:
            raise RuntimeError("Market not found")
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(market, key, value)
        await self._uow.commit()
        return market

    async def delete_market(self, seller_id: UUID) -> None:
        market = await self._repository.get_by_seller_id(seller_id=seller_id)
        if not market:
            raise RuntimeError("Market not found")
        await self._repository.delete(id=market.id)
        await self._uow.commit()

    async def get_market_by_seller(self, seller_id: UUID) -> SellerInfo:
        market = await self._repository.get_by_seller_id(seller_id=seller_id)
        if not market:
            raise RuntimeError("Market not found")
        return market

    async def get_verified_markets(self, skip: int = 0, limit: int = 100) -> List[SellerInfo]:
        return await self._repository.get_verified(skip=skip, limit=limit)

    async def get_market(self, market_id: UUID) -> SellerInfo:
        market = await self._repository.get(id=market_id)
        if not market:
            raise RuntimeError("Market not found")
        return market

    async def get_unverified_markets(self, skip: int = 0, limit: int = 100) -> List[SellerInfo]:
        return await self._repository.get_unverified(skip=skip, limit=limit)

    async def verify_market(self, market_id: UUID) -> None:
        market = await self._repository.get(id=market_id)
        if not market:
            raise RuntimeError("Market not found")
        await self._repository.verify(market_id=market_id)