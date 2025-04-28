
from typing import Annotated
from fastapi import APIRouter, Depends, Query


from schemas.role import Roles
from services.user import BaseUserService
from schemas.user import UserBase
from services.auth import BaseAuthService, require_roles


router = APIRouter(
    tags=['Users'],    
)

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