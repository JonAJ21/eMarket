from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres import get_session
from services.seller import SellerService, BaseSellerService

def get_seller_service(session: AsyncSession = Depends(get_session)) -> BaseSellerService:
    return SellerService(session=session) 