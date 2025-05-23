from typing import List
from fastapi import APIRouter, HTTPException, Query
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithSubcategories
from services.category_service import CategoryService

router = APIRouter()
category_service = CategoryService()

@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    try:
        return await category_service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryWithSubcategories)
async def get_category(category_id: str):
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    subcategories = await category_service.get_subcategories(category_id)
    return CategoryWithSubcategories(**category.dict(), subcategories=subcategories)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryUpdate):
    try:
        updated_category = await category_service.update_category(category_id, category)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
async def delete_category(category_id: str):
    try:
        if not await category_service.delete_category(category_id):
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return await category_service.list_categories(skip, limit)

@router.get("/{category_id}/subcategories", response_model=List[CategoryResponse])
async def get_subcategories(category_id: str):
    return await category_service.get_subcategories(category_id)

@router.get("/root/", response_model=List[CategoryResponse])
async def get_root_categories():
    return await category_service.get_root_categories() 