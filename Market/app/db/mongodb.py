from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Type, TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime
from core.config import settings
from metrics.decorators import cart_items_count

T = TypeVar('T', bound=BaseModel)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.db = cls.client[settings.mongodb_db_name]

    @classmethod
    async def close_database_connection(cls):
        if cls.client:
            cls.client.close()

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection_name = collection_name
        self.model_class = model_class
        self._collection = None

    @property
    def collection(self):
        if MongoDB.client is None or MongoDB.db is None:
            raise RuntimeError("MongoDB client is not initialized. Make sure to call connect_to_database() first.")
        if self._collection is None:
            self._collection = MongoDB.db[self.collection_name]
        return self._collection

    async def create(self, item: T) -> T:
        item_dict = item.model_dump(by_alias=True)
        result = await self.collection.insert_one(item_dict)
        if self.collection_name == "carts":
            cart_items_count.labels(user_id=item.user_id).set(len(item.items))
        return self.model_class(**item_dict)

    async def get_by_id(self, item_id: str) -> Optional[T]:
        item = await self.collection.find_one({"_id": item_id})
        if item:
            if "created_at" not in item:
                item["created_at"] = datetime.utcnow()
            if "updated_at" not in item:
                item["updated_at"] = datetime.utcnow()
            # Преобразуем _id в строку, если это ObjectId
            if "_id" in item and not isinstance(item["_id"], str):
                item["_id"] = str(item["_id"])
        return self.model_class(**item) if item else None

    async def update(self, item_id: str, item: T) -> Optional[T]:
        item_dict = item.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.update_one(
            {"_id": item_id},
            {"$set": item_dict}
        )
        if result.modified_count:
            if self.collection_name == "carts":
                cart_items_count.labels(user_id=item.user_id).set(len(item.items))
            return await self.get_by_id(item_id)
        return None

    async def delete(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": item_id})
        return result.deleted_count > 0

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        cursor = self.collection.find().skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        for item in items:
            if "created_at" not in item:
                item["created_at"] = datetime.utcnow()
            if "updated_at" not in item:
                item["updated_at"] = datetime.utcnow()
            if "seller_id" not in item:
                item["seller_id"] = "default_seller"
            # Преобразуем _id в строку, если это ObjectId
            if "_id" in item and not isinstance(item["_id"], str):
                item["_id"] = str(item["_id"])
        return [self.model_class(**item) for item in items]

mongodb = MongoDB() 