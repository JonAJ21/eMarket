from functools import cache

from fastapi import Depends
from async_fastapi_jwt_auth import AuthJWT

from storages.token import BaseTokenStorage
from services.user import BaseUserService
from services.auth import JWTAuthService
from services.auth import BaseAuthService
from dependencies.registrator import add_factory_to_mapper


@add_factory_to_mapper(BaseAuthService)
@cache
def create_auth_service(
    auth_jwt: AuthJWT = Depends(),
    token_storage: BaseTokenStorage = Depends(),
    user_service: BaseUserService = Depends(),
) -> BaseAuthService:
    return JWTAuthService(
        auth_jwt_service=auth_jwt,
        token_storage=token_storage,
        user_service=user_service,
    )