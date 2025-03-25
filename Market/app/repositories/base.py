from abc import ABC, abstractmethod

class BaseRepository(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs):
        ...
        
    @abstractmethod
    async def gets(self, *args, **kwargs):
        ...
        
    @abstractmethod
    async def insert(self, *args, **kwargs):
        ...
    
    @abstractmethod
    async def delete(self, *args, **kwargs):
        ...