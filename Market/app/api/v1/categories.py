from typing import List
from fastapi import APIRouter, HTTPException, Query
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithSubcategories
from services.category_service import CategoryService
from metrics.decorators import track_category_metrics, products_in_category

router = APIRouter()
category_service = CategoryService()

@router.post("/", response_model=CategoryResponse)
@track_category_metrics(operation_type="create")
async def create_category(category: CategoryCreate):
    try:
        result = await category_service.create_category(category)
        products_in_category.labels(category_id=str(result.id)).set(0)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryWithSubcategories)
@track_category_metrics(operation_type="get")
async def get_category(category_id: str):
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    subcategories = await category_service.get_subcategories(category_id)
    return CategoryWithSubcategories(**category.dict(), subcategories=subcategories)

@router.put("/{category_id}", response_model=CategoryResponse)
@track_category_metrics(operation_type="update")
async def update_category(category_id: str, category: CategoryUpdate):
    try:
        updated_category = await category_service.update_category(category_id, category)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
@track_category_metrics(operation_type="delete")
async def delete_category(category_id: str):
    try:
        if not await category_service.delete_category(category_id):
            raise HTTPException(status_code=404, detail="Category not found")
        products_in_category.labels(category_id=category_id).set(0)
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CategoryResponse])
@track_category_metrics(operation_type="list")
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return await category_service.list_categories(skip, limit)

@router.get("/{category_id}/subcategories", response_model=List[CategoryResponse])
@track_category_metrics(operation_type="get_subcategories")
async def get_subcategories(category_id: str):
    return await category_service.get_subcategories(category_id)

@router.get("/root/", response_model=List[CategoryResponse])
@track_category_metrics(operation_type="get_root")
async def get_root_categories():
    return await category_service.get_root_categories() 