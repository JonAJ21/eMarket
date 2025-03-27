from typing import Any, Generic, List, Type

from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.cache import BaseCacheService
from schemas.result import CreateSchemaType, ModelType
from repositories.base import BaseRepository


class PostgreRepository(BaseRepository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self._model = model
        self._session = session
        
    async def get(self, *, id: Any) -> ModelType | None:
        statement = select(self._model).where(self._model.id == id)
        return (await self._session.execute(statement)).scalar_one_or_none()
    
    async def gets(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        statement = select(self._model).order_by().offset(skip).limit(limit)
        return (await self._session.execute(statement)).scalars().all()
    
    async def insert(self, *, data: CreateSchemaType) -> ModelType:
        raw_obj = jsonable_encoder(data)
        db_obj = self._model(**raw_obj)
        self._session.add(db_obj)
        return db_obj
    
    async def delete(self, *, id: Any) -> None:
        statement = delete(self._model).where(self._model.id == id)
        await self._session.execute(statement)
        
        
class CachedPostgreRepository(
    PostgreRepository[ModelType, CreateSchemaType],
    Generic[ModelType, CreateSchemaType]
):
    def __init__(
        self, session: AsyncSession,
        model: Type[ModelType], cache_service: BaseCacheService
    ):
        self._session = session
        self._model = model
        self._cache_service = cache_service
        
    async def get(self, *, id: Any) -> ModelType | None:
        key = f"{self._model.__name__}_{id}"
        document = await self._cache_service.get(key=key)
        if not document:
            document = await super().get(id=id)
        return document
    
    async def gets(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return await super().gets(skip=skip, limit=limit)
    
    async def insert(self, *, body: CreateSchemaType) -> ModelType:
        return await super().insert(body=body)
    
    async def delete(self, *, id: Any) -> None:
        await super().delete(id=id)