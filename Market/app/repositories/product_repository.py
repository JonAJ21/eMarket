from typing import List, Optional
from schemas.product import ProductInDB
from db.mongodb import BaseRepository

class ProductRepository(BaseRepository[ProductInDB]):
    def __init__(self):
        super().__init__("products", ProductInDB)

    async def get_by_category(self, category_id: str) -> List[ProductInDB]:
        cursor = self.collection.find({"category_id": category_id})
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items]

    async def search_products(self, query: str) -> List[ProductInDB]:
        cursor = self.collection.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        })
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items] 