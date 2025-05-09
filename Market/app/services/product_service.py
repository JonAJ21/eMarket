from typing import List, Optional
from bson import ObjectId
from ..models.product import Product
from ..repositories.product_repository import ProductRepository
from ..repositories.category_repository import CategoryRepository

class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.category_repo = CategoryRepository()

    async def create_product(self, product: Product) -> Product:
        # Проверяем существование категории
        category = await self.category_repo.get_by_id(str(product.category_id))
        if not category:
            raise ValueError("Category not found")
        return await self.product_repo.create(product)

    async def get_product(self, product_id: str) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def update_product(self, product_id: str, product: Product) -> Optional[Product]:
        # Проверяем существование категории при обновлении
        if product.category_id:
            category = await self.category_repo.get_by_id(str(product.category_id))
            if not category:
                raise ValueError("Category not found")
        return await self.product_repo.update(product_id, product)

    async def delete_product(self, product_id: str) -> bool:
        return await self.product_repo.delete(product_id)

    async def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return await self.product_repo.list(skip, limit)

    async def get_products_by_category(self, category_id: str) -> List[Product]:
        return await self.product_repo.get_by_category(category_id)

    async def search_products(self, query: str) -> List[Product]:
        return await self.product_repo.search_products(query) 