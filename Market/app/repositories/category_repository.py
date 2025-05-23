from typing import List, Optional
from bson import ObjectId
from schemas.category import CategoryInDB
from db.mongodb import BaseRepository

class CategoryRepository(BaseRepository[CategoryInDB]):
    def __init__(self):
        super().__init__("categories", CategoryInDB)

    async def get_by_parent(self, parent_id: str) -> List[CategoryInDB]:
        cursor = self.collection.find({"parent_id": parent_id})
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items]

    async def get_root_categories(self) -> List[CategoryInDB]:
        cursor = self.collection.find({"parent_id": None})
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items] 