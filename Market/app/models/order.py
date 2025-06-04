from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from schemas.payment import Order, OrderCreate, OrderUpdate, OrderStatus

class OrderModel:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.orders

    async def create(self, order: OrderCreate) -> Order:
        order_dict = order.model_dump(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(order_dict)
        created_order = await self.collection.find_one({"_id": result.inserted_id})
        return Order(**created_order)

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        order = await self.collection.find_one({"_id": ObjectId(order_id)})
        return Order(**order) if order else None

    async def get_by_user_id(self, user_id: str) -> List[Order]:
        cursor = self.collection.find({"user_id": user_id})
        orders = await cursor.to_list(length=None)
        return [Order(**order) for order in orders]

    async def get_by_payment_id(self, payment_id: str) -> Optional[Order]:
        order = await self.collection.find_one({"payment_id": payment_id})
        return Order(**order) if order else None

    async def update(self, order_id: str, update_data: OrderUpdate) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        update_dict = {k: v for k, v in update_data.model_dump(by_alias=True, exclude_unset=True).items()}
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_dict}
            )
        return await self.get_by_id(order_id)

    async def update_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return await self.get_by_id(order_id)
