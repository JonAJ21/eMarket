from typing import List, Optional
from datetime import datetime
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository

class ProductService:
    def __init__(self):
        self._product_repo = None
        self._category_repo = None

    @property
    def product_repo(self) -> ProductRepository:
        if self._product_repo is None:
            self._product_repo = ProductRepository()
        return self._product_repo

    @property
    def category_repo(self) -> CategoryRepository:
        if self._category_repo is None:
            self._category_repo = CategoryRepository()
        return self._category_repo

    async def create_product(self, product: ProductCreate) -> Product:
        # Проверяем существование категории
        category = await self.category_repo.get_by_id(product.category_id)
        if not category:
            raise ValueError("Category not found")
            
        # Создаем модель Product из ProductCreate
        product_model = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            stock=product.stock,
            images=product.images,
            seller_id=product.seller_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.product_repo.create(product_model)

    async def get_product(self, product_id: str) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def update_product(self, product_id: str, product: ProductUpdate) -> Optional[Product]:
        # Получаем существующий продукт
        existing_product = await self.product_repo.get_by_id(product_id)
        if not existing_product:
            return None

        # Проверяем существование категории при обновлении
        if product.category_id:
            category = await self.category_repo.get_by_id(product.category_id)
            if not category:
                raise ValueError("Category not found")

        # Обновляем поля
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_product, field, value)
        existing_product.updated_at = datetime.utcnow()

        return await self.product_repo.update(product_id, existing_product)

    async def delete_product(self, product_id: str) -> bool:
        return await self.product_repo.delete(product_id)

    async def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return await self.product_repo.list(skip, limit)

    async def get_products_by_category(self, category_id: str) -> List[Product]:
        return await self.product_repo.get_by_category(category_id)

    async def search_products(self, query: str) -> List[Product]:
        return await self.product_repo.search_products(query) 