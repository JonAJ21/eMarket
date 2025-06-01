from typing import List
from fastapi import APIRouter, HTTPException, Query
from schemas.product import ProductCreate, ProductUpdate, ProductResponse
from services.product_service import ProductService
from metrics.decorators import track_product_metrics, products_in_stock

router = APIRouter()
product_service = ProductService()

@router.post("/", response_model=ProductResponse)
@track_product_metrics(operation_type="create")
async def create_product(product: ProductCreate):
    try:
        result = await product_service.create_product(product)
        products_in_stock.labels(product_id=str(result.id)).set(result.stock)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
@track_product_metrics(operation_type="get")
async def get_product(product_id: str):
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
@track_product_metrics(operation_type="update")
async def update_product(product_id: str, product: ProductUpdate):
    try:
        updated_product = await product_service.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        products_in_stock.labels(product_id=product_id).set(updated_product.stock)
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}")
@track_product_metrics(operation_type="delete")
async def delete_product(product_id: str):
    if not await product_service.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    products_in_stock.labels(product_id=product_id).set(0)
    return {"message": "Product deleted successfully"}

@router.get("/", response_model=List[ProductResponse])
@track_product_metrics(operation_type="list")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return await product_service.list_products(skip, limit)

@router.get("/category/{category_id}", response_model=List[ProductResponse])
@track_product_metrics(operation_type="list_by_category")
async def get_products_by_category(category_id: str):
    return await product_service.get_products_by_category(category_id)

@router.get("/search/", response_model=List[ProductResponse])
@track_product_metrics(operation_type="search")
async def search_products(query: str):
    return await product_service.search_products(query) 