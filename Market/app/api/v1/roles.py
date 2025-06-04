from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from typing import List, Optional
from uuid import UUID
from schemas.role import RoleCreateDTO, RoleUpdateDTO, Roles
from services.role import BaseRoleService
from services.auth import BaseAuthService, require_roles
from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

class SuccessMessage(BaseModel):
    message: str = "Success"

router = APIRouter(tags=["Roles"])

@router.get("/", response_model=List[RoleResponse], summary="Get all roles", description="Get a list of all roles")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_roles(
    role_service: BaseRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    return await role_service.get_roles()

@router.get("/{role_id}", response_model=RoleResponse, summary="Get role by ID", description="Get information about the role_id role")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def get_role(
    role_id: UUID = Path(...),
    role_service: BaseRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    role = await role_service.get_role(role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/", response_model=RoleResponse, summary="Add a role", description="Add a role with the name and description")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def create_role(
    dto: RoleCreateDTO = Body(...),
    role_service: BaseRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    role = await role_service.create_role(dto=dto)
    return role

@router.put("/{role_id}", response_model=RoleResponse, summary="Update a role", description="Change the name and description of the role")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def update_role(
    role_id: UUID = Path(...),
    dto: RoleCreateDTO = Body(...),
    role_service: BaseRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    update_dto = RoleUpdateDTO(role_id=str(role_id), name=dto.name, description=dto.description)
    role = await role_service.update_role(dto=update_dto)
    return role

@router.delete("/{role_id}", response_model=SuccessMessage, summary="Delete a role", description="Delete the role_id role")
@require_roles([Roles.ADMIN, Roles.SUPER_ADMIN])
async def delete_role(
    role_id: UUID = Path(...),
    role_service: BaseRoleService = Depends(),
    auth_service: BaseAuthService = Depends(),
):
    await role_service.delete_role(role_id=role_id)
    return SuccessMessage() 