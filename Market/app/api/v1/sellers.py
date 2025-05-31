from fastapi import APIRouter, Depends, Path, Body, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from schemas.seller import SellerCreateDTO
from pydantic import BaseModel
from services.auth import BaseAuthService, require_roles
from schemas.role import Roles

# --- Response Schemas ---
class SellerInfoResponse(BaseModel):
    user_id: UUID
    name: str
    address: str
    postal_code: str
    phone: Optional[str]
    inn: str
    kpp: str
    payment_account: str
    correspondent_account: str
    bank: str
    bik: str
    is_verified: bool

class SuccessMessage(BaseModel):
    message: str = "Success"

router = APIRouter(tags=["Markets"])

# 1. Create a store (not verified)
@router.post("/", response_model=SellerInfoResponse, summary="Create a store", description="Create a store (not verified)")
async def create_store(
    dto: SellerCreateDTO = Body(...),
    auth_service: BaseAuthService = Depends(),
    seller_service = Depends(),
):
    user = await auth_service.get_user()
    # Implement: seller = await seller_service.create_store(user_id=user.id, dto=dto)
    # For now, just return dummy
    return SellerInfoResponse(user_id=user.id, **dto.dict(), is_verified=False)

# 2. Update information about the store (your own)
@router.put("/", response_model=SellerInfoResponse, summary="Update your store", description="Update information about the store (your own)")
async def update_store(
    dto: SellerCreateDTO = Body(...),
    auth_service: BaseAuthService = Depends(),
    seller_service = Depends(),
):
    user = await auth_service.get_user()
    # Implement: seller = await seller_service.update_store(user_id=user.id, dto=dto)
    return SellerInfoResponse(user_id=user.id, **dto.dict(), is_verified=False)

# 3. Delete the store (your own)
@router.delete("/", response_model=SuccessMessage, summary="Delete your store", description="Delete the store (your own)")
async def delete_store(
    auth_service: BaseAuthService = Depends(),
    seller_service = Depends(),
):
    user = await auth_service.get_user()
    # Implement: await seller_service.delete_store(user_id=user.id)
    return SuccessMessage()

# 4. View information about the store (your own)
@router.get("/profile", response_model=SellerInfoResponse, summary="View your store", description="View information about the store (your own)")
async def get_own_store(
    auth_service: BaseAuthService = Depends(),
    seller_service = Depends(),
):
    user = await auth_service.get_user()
    # Implement: seller = await seller_service.get_store_by_user(user_id=user.id)
    return SellerInfoResponse(user_id=user.id, name="Store", address="Address", postal_code="000000", phone=None, inn="", kpp="", payment_account="", correspondent_account="", bank="", bik="", is_verified=False)

# 5. Get information about the limit of stores confirmed by the administration, starting with skip
@router.get("/", response_model=List[SellerInfoResponse], summary="List verified stores", description="Get information about the limit of stores confirmed by the administration, starting with skip")
async def list_verified_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    seller_service = Depends(),
):
    # Implement: sellers = await seller_service.list_verified_stores(skip=skip, limit=limit)
    return []

# 6. Get information about the store's market_id
@router.get("/{market_id}", response_model=SellerInfoResponse, summary="Get store by ID", description="Get information about the store's market_id")
async def get_store_by_id(
    market_id: UUID = Path(...),
    seller_service = Depends(),
):
    # Implement: seller = await seller_service.get_store_by_id(market_id)
    return SellerInfoResponse(user_id=market_id, name="Store", address="Address", postal_code="000000", phone=None, inn="", kpp="", payment_account="", correspondent_account="", bank="", bik="", is_verified=False)

# 7. Get information about the limit of unconfirmed stores starting with skip
@router.get("/unverified", response_model=List[SellerInfoResponse], summary="List unverified stores", description="Get information about the limit of unconfirmed stores starting with skip")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def list_unverified_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    seller_service = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    # Implement: sellers = await seller_service.list_unverified_stores(skip=skip, limit=limit)
    return []

# 8. Verify the store
@router.put("/{market_id}/verify", response_model=SuccessMessage, summary="Verify a store", description="Verify the store")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def verify_store(
    market_id: UUID = Path(...),
    seller_service = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    # Implement: await seller_service.verify_store(market_id)
    return SuccessMessage() 