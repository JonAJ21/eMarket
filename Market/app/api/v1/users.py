from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from uuid import UUID
from datetime import datetime

from schemas.role import Roles
from services.user import BaseUserService
from schemas.user import UserBase, UserUpdatePasswordDTO, UserUpdatePersonalDTO, UserCreateDTO, UserResponse, UserUpdateDTO, UserListResponse, UserHistoryResponse
from services.auth import BaseAuthService, require_roles
from schemas.result import GenericResult
from services.user_role import BaseUserRoleService
from dependencies.services.user_service_factory import get_user_service

# --- Response schemas ---
from pydantic import BaseModel

class UserDetail(BaseModel):
    id: UUID
    login: str
    first_name: Optional[str]
    last_name: Optional[str]
    fathers_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserHistoryResponse(BaseModel):
    user_id: UUID
    attempted_at: datetime
    user_agent: Optional[str]
    user_device_type: Optional[str]
    is_success: bool

class SuccessMessage(BaseModel):
    message: str = "Success"

# --- Endpoints ---

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

@router.get("/{user_id}", response_model=UserDetail, tags=["Users"], summary="Get user by ID", description="Get user information by user_id")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_user_by_id(
    user_id: UUID = Path(...),
    user_service: BaseUserService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    user = await user_service.get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/profile", response_model=UserDetail, tags=["Users"], summary="Get active user profile", description="Get information about the active user")
async def get_profile(
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    return user

@router.get("/{user_id}/history", response_model=List[UserHistoryResponse], tags=["Users"], summary="Get user history", description="Get history of user visits by user_id")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_user_history(
    user_id: UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    user_service: BaseUserService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    return await user_service.get_user_history(user_id=user_id, skip=skip, limit=limit)

@router.get("/profile/history", response_model=List[UserHistoryResponse], tags=["Users"], summary="Get active user history", description="Get history of the active user")
async def get_profile_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    return await user_service.get_user_history(user_id=user.id, skip=skip, limit=limit)

@router.put("/profile/login", response_model=SuccessMessage, tags=["Users"], summary="Change login")
async def change_login(
    login: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    # Implement logic to change login
    # await user_service.change_login(user_id=user.id, login=login)
    return SuccessMessage()

@router.put("/profile/password", response_model=SuccessMessage, tags=["Users"], summary="Change password")
async def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    dto = UserUpdatePasswordDTO(user_id=user.id, old_password=old_password, new_password=new_password)
    await user_service.update_password(dto=dto)
    return SuccessMessage()

@router.put("/profile/email", response_model=SuccessMessage, tags=["Users"], summary="Change email")
async def change_email(
    email: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    # Implement logic to change email
    # await user_service.change_email(user_id=user.id, email=email)
    return SuccessMessage()

@router.put("/profile/name", response_model=SuccessMessage, tags=["Users"], summary="Change full name")
async def change_name(
    first_name: str = Body(...),
    last_name: str = Body(...),
    fathers_name: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    dto = UserUpdatePersonalDTO(user_id=user.id, first_name=first_name, last_name=last_name, fathers_name=fathers_name)
    await user_service.update_personal(dto=dto)
    return SuccessMessage()

@router.put("/profile/phone", response_model=SuccessMessage, tags=["Users"], summary="Change phone")
async def change_phone(
    phone: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    # Implement logic to change phone
    # await user_service.change_phone(user_id=user.id, phone=phone)
    return SuccessMessage()

@router.put("/{user_id}/role/{role_id}", response_model=SuccessMessage, tags=["Users"], summary="Add role to user")
# @require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def add_role_to_user(
    user_id: UUID = Path(...),
    role_id: UUID = Path(...),
    user_role_service: BaseUserRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    await user_role_service.assign_role_to_user(user_id=user_id, role_id=role_id)
    return SuccessMessage()

@router.delete("/{user_id}/role/{role_id}", response_model=SuccessMessage, tags=["Users"], summary="Remove role from user")
# @require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def remove_role_from_user(
    user_id: UUID = Path(...),
    role_id: UUID = Path(...),
    user_role_service: BaseUserRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    await user_role_service.remove_role_from_user(user_id=user_id, role_id=role_id)
    return SuccessMessage()

@router.delete("/{user_id}", response_model=SuccessMessage, tags=["Users"], summary="Delete user by ID")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def delete_user_by_id(
    user_id: UUID = Path(...),
    user_service: BaseUserService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    await user_service.delete_user(user_id=user_id)
    return SuccessMessage()

@router.delete("/profile", response_model=SuccessMessage, tags=["Users"], summary="Delete active user profile")
async def delete_profile(
    password: str = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(),
):
    user = await auth_service.get_user()
    # Implement logic to check password and delete user
    # await user_service.delete_user(user_id=user.id)
    return SuccessMessage()

@router.get("/me", response_model=UserResponse, summary="Get your profile")
async def get_own_profile(
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(get_user_service),
):
    user = await auth_service.get_user()
    result = await user_service.get_user_by_id(user.id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.put("/me", response_model=UserResponse, summary="Update your profile")
async def update_own_profile(
    dto: UserUpdateDTO = Body(...),
    auth_service: BaseAuthService = Depends(),
    user_service: BaseUserService = Depends(get_user_service),
):
    user = await auth_service.get_user()
    result = await user_service.update_user(user.id, dto)
    return result

@router.get("/", response_model=UserListResponse, summary="List users")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(),
):
    return await user_service.list_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserResponse, summary="Update user by ID")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def update_user_by_id(
    user_id: UUID = Path(...),
    dto: UserUpdateDTO = Body(...),
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(),
):
    return await user_service.update_user(user_id, dto)

@router.delete("/{user_id}", summary="Delete user by ID")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def delete_user_by_id(
    user_id: UUID = Path(...),
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(),
):
    await user_service.delete_user(user_id)
    return {"message": "Success"}

@router.put("/{user_id}/assign-role", summary="Assign role to user")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def assign_role(
    user_id: UUID = Path(...),
    role_id: UUID = Body(..., embed=True),
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(),
):
    await user_service.assign_role(user_id, role_id)
    return {"message": "Success"}

@router.get("/{user_id}/history", response_model=List[UserHistoryResponse], summary="Get user history")
async def get_user_history(
    user_id: UUID = Path(...),
    user_service: BaseUserService = Depends(get_user_service),
    auth_service: BaseAuthService = Depends(),
):
    current_user = await auth_service.get_user()
    if current_user.id != user_id and current_user.role_id not in [Roles.ADMIN, Roles.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await user_service.get_user_history(user_id)