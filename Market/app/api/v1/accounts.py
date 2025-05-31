from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Response, status
from fastapi.responses import JSONResponse
from redis import Redis

from services.pubsub import BasePubSub
from db.redis import get_redis
from services.auth import BaseAuthService
from schemas.auth import UserLoginDTO, UserLogout
from schemas.result import GenericResult
from services.user import BaseUserService
from core.extensions import build_dependencies
from models.user import User
from schemas.user import UserBase, UserCreateDTO
from schemas.token import Token


from uuid import uuid4

router = APIRouter(
    tags=["Accounts"],
)

@router.post(
    "/register",
    response_model=UserBase,
    description="Register new user",
    summary="Creating account for new user",
    dependencies=build_dependencies(),
)
async def register(
    user_dto: UserCreateDTO,
    user_service: BaseUserService = Depends(),
    pubsub: BasePubSub = Depends()
) -> User:
    try:
        result: User = await user_service.create_user(dto=user_dto)
        await pubsub.publish("notifications", result.login)
        return result
    except Exception as e:
        await pubsub.publish("notifications", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
    pubsub: BasePubSub = Depends()
):
    try:
        dto.user_agent = user_agent
        token: Token = await auth.login(dto=dto)
        if not token:
            await pubsub.publish("notifications", "login or/and password incorrect")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="login or/and password incorrect"
            )
    except RuntimeError as e:
        await pubsub.publish("notifications", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await pubsub.publish("notifications", f"{token.access_token[:20]}...")
    return token

@router.post(
    "/refresh",
    response_model=Token,
    description="Issuing new tokens if the access token is expired",
    response_description="Pair of tokens access and refresh",
    dependencies=build_dependencies(),
)
async def refresh(
    auth_service: BaseAuthService = Depends(),
    pubsub: BasePubSub = Depends()
):  
    await pubsub.publish("notifications", "refresh")
    return (await auth_service.refresh())

@router.post(
    "/logout",
    response_model=UserLogout,
    description="User logout",
    summary="User JWT logout",
    response_description="Logged out",
    dependencies=build_dependencies(),
)
async def logout(
    auth_service: BaseAuthService = Depends(),
    pubsub: BasePubSub = Depends()
):
    await auth_service.logout()
    await pubsub.publish("notifications", "Logged out")
    return UserLogout(message="Logged out")