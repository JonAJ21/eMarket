from abc import ABC, abstractmethod
from datetime import UTC, datetime
from functools import wraps
from time import time
from typing import Any

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import JWTDecodeError, MissingTokenError
from fastapi import Depends, HTTPException, Response, status

from models.user import User
from schemas.user import UserDeviceType, UserHistoryCreateDTO
from services.user import BaseUserService
from storages.token import BaseTokenStorage
from schemas.auth import UserLoginDTO
from schemas.result import Error, GenericResult, Result
from schemas.token import Token, TokenJTI

class BaseAuthService(ABC):
    @abstractmethod
    async def login(self, *, dto: UserLoginDTO) -> Token:
        ...
        
    @abstractmethod
    async def login_by_oauth(self, *, login: str) -> Token:
        ...
        
    @abstractmethod
    async def logout(self) -> None:
        ...
        
    @abstractmethod
    async def refresh(self) -> Token: 
        ...
        
    @abstractmethod
    async def require_auth(self) -> None:
        ...
        
    @abstractmethod
    async def optional_auth(self):
        ...
        
    @abstractmethod
    async def get_user(self) -> User:
        ...
        
    @abstractmethod
    async def get_auth_user(self, token: str) -> User:
        ...
        

class JWTAuthService(BaseAuthService):
    def __init__(
        self,
        auth_jwt_service: AuthJWT,
        token_storage: BaseTokenStorage,
        user_service: BaseUserService
    ):
        self._auth_jwt_service = auth_jwt_service
        self._token_storage = token_storage
        self._user_service = user_service
        
    async def _generate_token(self, user_id: Any) -> Token:
        return Token(
            access_token=await self._auth_jwt_service.create_access_token(subject=str(user_id)),
            refresh_token=await self._auth_jwt_service.create_refresh_token(subject=str(user_id))
        )
    
    async def _get_jti(self):
        return (await self._auth_jwt_service.get_raw_jwt())["jti"]
    
    async def _check_token_expiracy(self) -> bool:
        jti = await self._get_jti()
        return await self._token_storage.check_expiration(jti=jti)
    
    async def _refresh_token_required(self):
        try:
            await self._auth_jwt_service.jwt_refresh_token_required()
            if await self._check_token_expiracy():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTDecodeError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
        except MissingTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found")
        
    async def _decode_token(self, token: str):
        try:
            return await self._auth_jwt_service.get_raw_jwt(token)
        except JWTDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
            )
            
    async def login(self, *, dto: UserLoginDTO) -> GenericResult[Token]:
        user: User = await self._user_service.get_user_by_login(login=dto.login)
        if not user or not user.check_password(dto.password):
            return GenericResult.failure(Error(message="Wrong password or login", code="auth_failed"))
        user_history = UserHistoryCreateDTO(
            user_id=user.id,
            user_agent=dto.user_agent,
            user_device_type=UserDeviceType.web,
            attempted_at=datetime.now(),
            is_success=True
        )
        await self._user_service.insert_user_login(dto=user_history)
        tokens = await self._generate_token(user_id=user.id)
        await self._auth_jwt_service.set_access_cookies(tokens.access_token)
        await self._auth_jwt_service.set_refresh_cookies(tokens.refresh_token)
        return GenericResult.success(tokens)
    
    async def login_by_oauth(self, *, login: str) -> GenericResult[Token]:
        user: User = await self._user_service.get_user_by_login(login=login)
        if not user:
            return GenericResult.failure(Error(message="User not found", code="user_not_found"))
        user_history = UserHistoryCreateDTO(
            user_id=user.id,
            user_agent="oauth2",
            user_device_type=UserDeviceType.web,
            attempted_at=datetime.now(),
            is_success=True
        )
        await self._user_service.insert_user_login(dto=user_history)
        tokens = await self._generate_token(user_id=user.id)
        await self._auth_jwt_service.set_access_cookies(tokens.access_token)
        await self._auth_jwt_service.set_refresh_cookies(tokens.refresh_token)
        return GenericResult.success(tokens)
    
    async def logout(self) -> None:
        await self.require_auth()
        access_jti = (await self._auth_jwt_service.get_raw_jwt())["jti"]
        await self._auth_jwt_service.unset_jwt_cookies()
        token_jti = TokenJTI(access_token_jti=access_jti, refresh_token_jti=None)
        return await self._token_storage.store_token(token_jti=token_jti)
        
        
    async def refresh(self) -> GenericResult[Token]:
        await self._refresh_token_required()
        refresh_jti = await self._get_jti()
        token_jti = TokenJTI(
            access_token_jti=None,
            refresh_token_jti=refresh_jti
        )
        await self._token_storage.store_token(token_jti=token_jti)
        user_subject = await self._auth_jwt_service.get_jwt_subject()
        tokens = await self._generate_token(user_id=user_subject)
        await self._auth_jwt_service.set_access_cookies(tokens.access_token)
        await self._auth_jwt_service.set_refresh_cookies(tokens.refresh_token)
        return GenericResult.success(tokens)
        
        
    async def require_auth(self) -> None:
        try:
            await self._auth_jwt_service.jwt_required()
            if await self._check_token_expiracy():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unathorized"
                )
        except JWTDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message
            )
        except MissingTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message
            )
            
    async def optional_auth(self):
        return await self._auth_jwt_service.jwt_optional()
    
    async def get_user(self) -> User:
        await self.require_auth()
        user_subject = await self._auth_jwt_service.get_jwt_subject()
        return await self._user_service.get_user(user_id=user_subject)
    
    async def get_auth_user(self, access_token: str) -> User:
        decoded = await self._decode_token(access_token)
        if decoded["exp"] <= time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is expired"
            )
        user_id = decoded["sub"]
        return await self._user_service.get_user(user_id=user_id)
    
def require_roles(roles: list[str]):
    def auth_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            auth_service = kwargs["auth_service"]
            current_user: User = await auth_service.get_user()
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            for role in current_user.roles:
                if role.name in roles:
                    return await func(*args, **kwargs)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User have not access"
            )

        return wrapper

    return auth_decorator 
        
    