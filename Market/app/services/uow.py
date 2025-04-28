from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

class BaseUnitOfWork(ABC):
    @abstractmethod
    async def commit(self, *args, **kwargs):
        ...
        
class SQLAlchemyUnitOfWork(BaseUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def commit(self, *args, **kwargs):
        return await self._session.commit()
    

