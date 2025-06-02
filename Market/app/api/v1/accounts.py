from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Response, status
from fastapi.responses import JSONResponse
from prometheus_client import Counter

from services.auth import BaseAuthService
from schemas.auth import UserLoginDTO, UserLogout
from schemas.result import GenericResult
from services.user import BaseUserService
from core.extensions import build_dependencies
from models.user import User
from schemas.user import UserBase, UserCreateDTO
from schemas.token import Token


router = APIRouter(
    tags=["Accounts"],
)


user_registration_counter = Counter(
    'user_registration_total', 'Total number of user registrations')
user_login_counter = Counter(
    'user_login_total', 'Total number of user logins')
user_logout_counter = Counter(
    'user_logout_total', 'Total number of user logouts')

@router.post(
    "/register",
    response_model=UserBase,
    description="Register new user",
    summary="Creating account for new user",
    dependencies=build_dependencies(),
)
async def register(
    user_dto: UserCreateDTO,
    user_service: BaseUserService = Depends()
) -> User:
    result: GenericResult[User] = await user_service.create_user(dto=user_dto)
    if result.is_success:
        user_registration_counter.inc()
        return result.response
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error.message)


@router.post(
    "/login",
    response_model=Token,
    description="User auth",
    summary="User JWT auth",
    response_description="Access and refresh tokens",
    dependencies=build_dependencies(),
)
async def login(
    dto: UserLoginDTO,
    user_agent: Annotated[str | None, Header()] = None,
    auth: BaseAuthService = Depends(),
):
    dto.user_agent = user_agent
    token: GenericResult[Token] = await auth.login(dto=dto)
    if not token.is_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="login or/and password incorrect"
        )
    user_login_counter.inc()
    return token.response

@router.post(
    "/refresh",
    response_model=Token,
    description="Issuing new tokens if the access token is expired",
    response_description="Pair of tokens access and refresh",
    dependencies=build_dependencies(),
)
async def refresh(
    auth_service: BaseAuthService = Depends(),
):
    return (await auth_service.refresh()).response

@router.post(
    "/logout",
    response_model=UserLogout,
    description="User logout",
    summary="User JWT logout",
    response_description="Logged out",
    dependencies=build_dependencies(),
)
async def logout(auth_service: BaseAuthService = Depends()):
    await auth_service.logout()
    user_logout_counter.inc()
    return UserLogout(message="Logged out")