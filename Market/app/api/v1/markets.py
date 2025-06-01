from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from schemas.seller import SellerInfoBase, SellerInfoCreateDTO, SellerInfoUpdateDTO
from services.seller import SellerInfoService
from services.auth import BaseAuthService, require_roles
from dependencies.services import get_seller_service
from async_fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/markets", tags=["markets"])

async def get_current_user_id(auth_jwt: AuthJWT = Depends()) -> UUID:
    await auth_jwt.jwt_required()
    return UUID(await auth_jwt.get_jwt_subject())

@router.post("/", response_model=SellerInfoBase, status_code=status.HTTP_201_CREATED)
async def create_market(
    dto: SellerInfoCreateDTO,
    seller_id: UUID = Depends(get_current_user_id),
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    try:
        return await seller_service.create_market(seller_id=seller_id, dto=dto)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/", response_model=SellerInfoBase)
async def update_market(
    dto: SellerInfoUpdateDTO,
    seller_id: UUID = Depends(get_current_user_id),
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    try:
        return await seller_service.update_market(seller_id=seller_id, dto=dto)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/", response_model=dict)
async def delete_market(
    seller_id: UUID = Depends(get_current_user_id),
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    try:
        await seller_service.delete_market(seller_id=seller_id)
        return {"message": "Success"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/profile", response_model=SellerInfoBase)
async def get_market_profile(
    seller_id: UUID = Depends(get_current_user_id),
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    try:
        return await seller_service.get_market_by_seller(seller_id=seller_id)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[SellerInfoBase])
async def get_verified_markets(
    skip: int = 0,
    limit: int = 100,
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    return await seller_service.get_verified_markets(skip=skip, limit=limit)

@router.get("/{market_id}", response_model=SellerInfoBase)
async def get_market(
    market_id: UUID,
    seller_service: SellerInfoService = Depends(get_seller_service)
):
    try:
        return await seller_service.get_market(market_id=market_id)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/unverified", response_model=List[SellerInfoBase])
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_unverified_markets(
    skip: int = 0,
    limit: int = 100,
    seller_service: SellerInfoService = Depends(get_seller_service),
    auth_service: BaseAuthService = Depends()
):
    return await seller_service.get_unverified_markets(skip=skip, limit=limit)

@router.put("/{market_id}/verify", response_model=dict)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def verify_market(
    market_id: UUID,
    seller_service: SellerInfoService = Depends(get_seller_service),
    auth_service: BaseAuthService = Depends()
):
    try:
        await seller_service.verify_market(market_id=market_id)
        return {"message": "Success"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))