from fastapi import APIRouter, Depends, Path, Body, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from schemas.seller import SellerCreateDTO
from pydantic import BaseModel
from services.auth import BaseAuthService, require_roles
from schemas.role import Roles
from dependencies.services.seller_service_factory import get_seller_service
from services.seller import BaseSellerService
from prometheus_client import Counter


market_create_counter = Counter('market_create_total', 'Total number of markets created')
market_update_counter = Counter('market_update_total', 'Total number of markets updated')
market_delete_counter = Counter('market_delete_total', 'Total number of markets deleted')
market_verify_counter = Counter('market_verify_total', 'Total number of markets verified')
market_list_counter = Counter('market_list_total', 'Total number of market list requests')

class SellerInfoResponse(BaseModel):
    user_id: UUID
    name: str
    address: str
    postal_code: str
    phone: Optional[str] = None
    inn: str
    kpp: str
    payment_account: str
    correspondent_account: str
    bank: str
    bik: str
    is_verified: bool

    class Config:
        from_attributes = True

class SuccessMessage(BaseModel):
    message: str = "Success"

router = APIRouter(tags=["Markets"])


@router.post("/", response_model=SellerInfoResponse, summary="Create a store", description="Create a store (not verified)")
async def create_store(
    dto: SellerCreateDTO = Body(...),
    auth_service: BaseAuthService = Depends(),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    user = await auth_service.get_user()
    try:
        seller = await seller_service.create_store(user_id=user.id, dto=dto)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    market_create_counter.inc()
    return SellerInfoResponse.from_orm(seller)

@router.put("/", response_model=SellerInfoResponse, summary="Update your store", description="Update information about the store (your own)")
async def update_store(
    dto: SellerCreateDTO = Body(...),
    auth_service: BaseAuthService = Depends(),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    user = await auth_service.get_user()
    seller = await seller_service.update_store(user_id=user.id, dto=dto)
    market_update_counter.inc()
    return SellerInfoResponse.from_orm(seller)


@router.delete("/", response_model=SuccessMessage, summary="Delete your store", description="Delete the store (your own)")
async def delete_store(
    auth_service: BaseAuthService = Depends(),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    user = await auth_service.get_user()
    await seller_service.delete_store(user_id=user.id)
    market_delete_counter.inc()
    return SuccessMessage()


@router.get("/unverified", response_model=List[SellerInfoResponse], summary="List unverified stores", description="Get information about the limit of unconfirmed stores starting with skip")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def list_unverified_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    seller_service: BaseSellerService = Depends(get_seller_service),
    auth_service: BaseAuthService = Depends(),
):
    sellers = await seller_service.list_unverified_stores(skip=skip, limit=limit)
    market_list_counter.inc()
    return [SellerInfoResponse.from_orm(s) for s in sellers]


@router.get("/profile", response_model=SellerInfoResponse, summary="View your store", description="View information about the store (your own)")
async def get_own_store(
    auth_service: BaseAuthService = Depends(),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    user = await auth_service.get_user()
    seller = await seller_service.get_store_by_user(user_id=user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Store not found")
    return SellerInfoResponse.from_orm(seller)


@router.get("/{market_id}", response_model=SellerInfoResponse, summary="Get store by ID", description="Get information about the store's market_id")
async def get_store_by_id(
    market_id: UUID = Path(...),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    seller = await seller_service.get_store_by_id(market_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Store not found")
    return SellerInfoResponse.from_orm(seller)


@router.get("/", response_model=List[SellerInfoResponse], summary="List verified stores", description="Get information about the limit of stores confirmed by the administration, starting with skip")
async def list_verified_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    seller_service: BaseSellerService = Depends(get_seller_service),
):
    sellers = await seller_service.list_verified_stores(skip=skip, limit=limit)
    market_list_counter.inc()
    return [SellerInfoResponse.from_orm(s) for s in sellers]


@router.put("/{market_id}/verify", response_model=SuccessMessage, summary="Verify a store", description="Verify the store")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def verify_store(
    market_id: UUID = Path(...),
    seller_service: BaseSellerService = Depends(get_seller_service),
    auth_service: BaseAuthService = Depends(),
):
    await seller_service.verify_store(market_id)
    market_verify_counter.inc()
    return SuccessMessage() 
