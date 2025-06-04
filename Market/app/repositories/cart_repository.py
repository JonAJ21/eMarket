from typing import List, Optional
from models.cart import Cart, CartItem
from db.mongodb import BaseRepository
from metrics.decorators import cart_items_count

class CartRepository(BaseRepository[Cart]):
    def __init__(self):
        super().__init__("carts", Cart)

    async def get_by_user(self, user_id: str) -> Optional[Cart]:
        cart = await self.collection.find_one({"user_id": user_id})
        if cart:
            cart_obj = self.model_class(**cart)
            cart_items_count.labels(user_id=user_id).set(len(cart_obj.items))
        return self.model_class(**cart) if cart else None

    async def add_item(self, user_id: str, item: CartItem) -> Optional[Cart]:
        cart = await self.get_by_user(user_id)
        if not cart:
            cart = Cart(user_id=user_id, items=[item])
            cart = await self.create(cart)
            cart_items_count.labels(user_id=user_id).set(len(cart.items))
            return cart

        # Проверяем, есть ли уже такой товар в корзине
        for existing_item in cart.items:
            if existing_item.product_id == item.product_id:
                existing_item.quantity += item.quantity
                cart = await self.update(str(cart.id), cart)
                cart_items_count.labels(user_id=user_id).set(len(cart.items))
                return cart

        cart.items.append(item)
        cart = await self.update(str(cart.id), cart)
        cart_items_count.labels(user_id=user_id).set(len(cart.items))
        return cart

    async def remove_item(self, user_id: str, product_id: str) -> Optional[Cart]:
        cart = await self.get_by_user(user_id)
        if not cart:
            return None

        cart.items = [item for item in cart.items if str(item.product_id) != product_id]
        cart = await self.update(str(cart.id), cart)
        if cart:
            cart_items_count.labels(user_id=user_id).set(len(cart.items))
        return cart

    async def update_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Optional[Cart]:
        cart = await self.get_by_user(user_id)
        if not cart:
            return None

        for item in cart.items:
            if str(item.product_id) == product_id:
                item.quantity = quantity
                cart = await self.update(str(cart.id), cart)
                if cart:
                    cart_items_count.labels(user_id=user_id).set(len(cart.items))
                return cart

        return cart 