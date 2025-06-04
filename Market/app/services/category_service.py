from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate
from repositories.category_repository import CategoryRepository

class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()

    async def create_category(self, category: CategoryCreate) -> Category:
        # Проверяем существование родительской категории
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if not parent:
                raise ValueError("Parent category not found")
        
        # Создаем модель Category из CategoryCreate
        category_model = Category(
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.category_repo.create(category_model)

    async def get_category(self, category_id: str) -> Optional[Category]:
        return await self.category_repo.get_by_id(category_id)

    async def update_category(self, category_id: str, category: CategoryUpdate) -> Optional[Category]:
        # Получаем существующую категорию
        existing_category = await self.category_repo.get_by_id(category_id)
        if not existing_category:
            return None

        # Проверяем существование родительской категории при обновлении
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if not parent:
                raise ValueError("Parent category not found")

        # Обновляем поля
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_category, field, value)
        existing_category.updated_at = datetime.utcnow()

        return await self.category_repo.update(category_id, existing_category)

    async def delete_category(self, category_id: str) -> bool:
        # Проверяем, нет ли подкатегорий
        subcategories = await self.category_repo.get_by_parent(category_id)
        if subcategories:
            raise ValueError("Cannot delete category with subcategories")
        return await self.category_repo.delete(category_id)

    async def list_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return await self.category_repo.list(skip, limit)

    async def get_subcategories(self, category_id: str) -> List[Category]:
        return await self.category_repo.get_by_parent(category_id)

    async def get_root_categories(self) -> List[Category]:
        return await self.category_repo.get_root_categories() 