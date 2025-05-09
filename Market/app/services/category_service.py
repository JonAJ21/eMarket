from typing import List, Optional
from bson import ObjectId
from ..models.category import Category
from ..repositories.category_repository import CategoryRepository

class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()

    async def create_category(self, category: Category) -> Category:
        # Проверяем существование родительской категории
        if category.parent_id:
            parent = await self.category_repo.get_by_id(str(category.parent_id))
            if not parent:
                raise ValueError("Parent category not found")
        return await self.category_repo.create(category)

    async def get_category(self, category_id: str) -> Optional[Category]:
        return await self.category_repo.get_by_id(category_id)

    async def update_category(self, category_id: str, category: Category) -> Optional[Category]:
        # Проверяем существование родительской категории при обновлении
        if category.parent_id:
            parent = await self.category_repo.get_by_id(str(category.parent_id))
            if not parent:
                raise ValueError("Parent category not found")
        return await self.category_repo.update(category_id, category)

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