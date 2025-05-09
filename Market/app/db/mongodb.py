from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Type, TypeVar, Generic
from pydantic import BaseModel
from bson import ObjectId

T = TypeVar('T', bound=BaseModel)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[str] = None

    @classmethod
    async def connect_to_database(cls, database_url: str, database_name: str):
        cls.client = AsyncIOMotorClient(database_url)
        cls.database = database_name

    @classmethod
    async def close_database_connection(cls):
        if cls.client:
            cls.client.close()

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection_name = collection_name
        self.model_class = model_class
        self.collection = MongoDB.client[MongoDB.database][collection_name]

    async def create(self, item: T) -> T:
        item_dict = item.model_dump(by_alias=True)
        result = await self.collection.insert_one(item_dict)
        item_dict["_id"] = result.inserted_id
        return self.model_class(**item_dict)

    async def get_by_id(self, item_id: str) -> Optional[T]:
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        return self.model_class(**item) if item else None

    async def update(self, item_id: str, item: T) -> Optional[T]:
        item_dict = item.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": item_dict}
        )
        if result.modified_count:
            return await self.get_by_id(item_id)
        return None

    async def delete(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        cursor = self.collection.find().skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [self.model_class(**item) for item in items] 