from typing import List, Optional
from schemas.review import ReviewInDB
from db.mongodb import BaseRepository

class ReviewRepository(BaseRepository[ReviewInDB]):
    def __init__(self):
        super().__init__("reviews", ReviewInDB)

    async def get_by_product(self, product_id: str) -> List[ReviewInDB]:
        cursor = self.collection.find({"product_id": product_id})
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items]

    async def get_by_user(self, user_id: str) -> List[ReviewInDB]:
        cursor = self.collection.find({"user_id": user_id})
        items = await cursor.to_list(length=None)
        return [self.model_class(**item) for item in items]

    async def get_average_rating(self, product_id: str) -> float:
        pipeline = [
            {"$match": {"product_id": product_id}},
            {"$group": {"_id": None, "average": {"$avg": "$rating"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["average"] if result else 0.0 