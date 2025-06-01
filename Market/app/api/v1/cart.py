from typing import List
from fastapi import APIRouter, HTTPException, Query
from schemas.cart import CartResponse, CartItemResponse, CartItemCreate, CartItemUpdate
from services.cart_service import CartService
from services.product_service import ProductService
from metrics.decorators import track_cart_metrics, cart_items_count

router = APIRouter()
cart_service = CartService()
product_service = ProductService()

@router.get("/{user_id}", response_model=CartResponse)
@track_cart_metrics(operation_type="get")
async def get_cart(user_id: str):
    cart = await cart_service.get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart_items_count.labels(user_id=user_id).set(len(cart.items))
    return cart

@router.post("/{user_id}/items", response_model=CartResponse)
@track_cart_metrics(operation_type="add")
async def add_to_cart(user_id: str, item: CartItemCreate):
    try:
        cart = await cart_service.add_to_cart(user_id, item.product_id, item.quantity)
        if not cart:
            raise HTTPException(status_code=404, detail="Failed to add item to cart")
        cart_items_count.labels(user_id=user_id).set(len(cart.items))
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/items/{product_id}", response_model=CartResponse)
@track_cart_metrics(operation_type="remove")
async def remove_from_cart(user_id: str, product_id: str):
    cart = await cart_service.remove_from_cart(user_id, product_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart or item not found")
    cart_items_count.labels(user_id=user_id).set(len(cart.items))
    return cart

@router.put("/{user_id}/items/{product_id}", response_model=CartResponse)
@track_cart_metrics(operation_type="update")
async def update_cart_item_quantity(
    user_id: str,
    product_id: str,
    item: CartItemUpdate
):
    try:
        cart = await cart_service.update_cart_item_quantity(user_id, product_id, item.quantity)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart or item not found")
        cart_items_count.labels(user_id=user_id).set(len(cart.items))
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
@track_cart_metrics(operation_type="clear")
async def clear_cart(user_id: str):
    cart = await cart_service.clear_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart_items_count.labels(user_id=user_id).set(0)
    return {"message": "Cart cleared successfully"}

@router.get("/{user_id}/items", response_model=List[CartItemResponse])
@track_cart_metrics(operation_type="get_items")
async def get_cart_items(user_id: str):
    cart = await cart_service.get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = []
    for item in cart.items:
        product = await product_service.get_product(str(item.product_id))
        if product:
            items.append(CartItemResponse(
                **item.dict(),
                product_name=product.name,
                product_price=product.price,
                total_price=product.price * item.quantity
            ))
    cart_items_count.labels(user_id=user_id).set(len(items))
    return items 