from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID

from schemas.role import Roles
from services.user import BaseUserService
from schemas.user import UserBase, UserUpdateNameDTO, UserUpdatePhoneDTO
from services.auth import BaseAuthService, require_roles
from dependencies.services import get_user_service
from async_fastapi_jwt_auth import AuthJWT


router = APIRouter(
    tags=['Users'],    
)

async def get_current_user_id(auth_jwt: AuthJWT = Depends()) -> UUID:
    await auth_jwt.jwt_required()
    return UUID(await auth_jwt.get_jwt_subject())

@router.get(
    "/",
    description="Retrieve information about all users in the system",
    response_model=list[UserBase],
    response_description="List of user accounts in the system",
    tags=["Users"],
)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_users(
    skip: Annotated[int, Query(description="Items to skip", ge=0)] = 0,
    limit: Annotated[int, Query(description="Pagination page size", ge=1)] = 10,
    user_service: BaseUserService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    return await user_service.get_users(skip=skip, limit=limit)

@router.put("/profile/name")
async def update_user_name(
    data: UserUpdateNameDTO,
    user_id: UUID = Depends(get_current_user_id),
    user_service: BaseUserService = Depends(get_user_service)
):
    try:
        await user_service.update_name(user_id=user_id, data=data)
        return {"message": "Name updated successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/profile/phone")
async def update_user_phone(
    data: UserUpdatePhoneDTO,
    user_id: UUID = Depends(get_current_user_id),
    user_service: BaseUserService = Depends(get_user_service)
):
    try:
        await user_service.update_phone(user_id=user_id, data=data)
        return {"message": "Phone updated successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))