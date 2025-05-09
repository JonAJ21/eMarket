from typing import List, Optional
from bson import ObjectId
from ..models.cart import Cart, CartItem
from ..repositories.cart_repository import CartRepository
from ..repositories.product_repository import ProductRepository

class CartService:
    def __init__(self):
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()

    async def get_cart(self, user_id: str) -> Optional[Cart]:
        return await self.cart_repo.get_by_user(user_id)

    async def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Optional[Cart]:
        # Проверяем существование товара и его наличие
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.stock < quantity:
            raise ValueError("Not enough stock")

        item = CartItem(product_id=ObjectId(product_id), quantity=quantity)
        return await self.cart_repo.add_item(user_id, item)

    async def remove_from_cart(self, user_id: str, product_id: str) -> Optional[Cart]:
        return await self.cart_repo.remove_item(user_id, product_id)

    async def update_cart_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Optional[Cart]:
        # Проверяем наличие товара
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.stock < quantity:
            raise ValueError("Not enough stock")

        return await self.cart_repo.update_item_quantity(user_id, product_id, quantity)

    async def clear_cart(self, user_id: str) -> Optional[Cart]:
        cart = await self.cart_repo.get_by_user(user_id)
        if cart:
            cart.items = []
            return await self.cart_repo.update(str(cart.id), cart)
        return None 