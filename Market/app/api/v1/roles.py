# Assume this exists in api/v1/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from schemas.role import RoleBase, RoleCreateDTO, RoleUpdateDTO, Roles
from services.role import RoleService
from services.auth import BaseAuthService, require_roles
from dependencies.services import get_role_service

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[RoleBase])
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    role_service: RoleService = Depends(get_role_service),
    auth_service: BaseAuthService = Depends()
):
    return await role_service.get_roles(skip=skip, limit=limit)

@router.get("/{role_id}", response_model=RoleBase)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    auth_service: BaseAuthService = Depends()
):
    try:
        return await role_service.get_role(role_id=role_id)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=RoleBase, status_code=status.HTTP_201_CREATED)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def create_role(
    dto: RoleCreateDTO,
    role_service: RoleService = Depends(get_role_service),
    auth_service: BaseAuthService = Depends()
):
    try:
        return await role_service.create_role(dto=dto)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{role_id}", response_model=RoleBase)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def update_role(
    role_id: UUID,
    dto: RoleUpdateDTO,
    role_service: RoleService = Depends(get_role_service),
    auth_service: BaseAuthService = Depends()
):
    try:
        return await role_service.update_role(role_id=role_id, dto=dto)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{role_id}", response_model=dict)
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    auth_service: BaseAuthService = Depends()
):
    try:
        await role_service.delete_role(role_id=role_id)
        return {"message": "Success"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))