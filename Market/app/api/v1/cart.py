from typing import List
from fastapi import APIRouter, HTTPException, Query
from ...schemas.cart import CartResponse, CartItemResponse
from ...services.cart_service import CartService
from ...services.product_service import ProductService

router = APIRouter()
cart_service = CartService()
product_service = ProductService()

@router.get("/{user_id}", response_model=CartResponse)
async def get_cart(user_id: str):
    cart = await cart_service.get_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("/{user_id}/items", response_model=CartResponse)
async def add_to_cart(user_id: str, product_id: str, quantity: int = Query(1, gt=0)):
    try:
        cart = await cart_service.add_to_cart(user_id, product_id, quantity)
        if not cart:
            raise HTTPException(status_code=404, detail="Failed to add item to cart")
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(user_id: str, product_id: str):
    cart = await cart_service.remove_from_cart(user_id, product_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart or item not found")
    return cart

@router.put("/{user_id}/items/{product_id}", response_model=CartResponse)
async def update_cart_item_quantity(
    user_id: str,
    product_id: str,
    quantity: int = Query(..., gt=0)
):
    try:
        cart = await cart_service.update_cart_item_quantity(user_id, product_id, quantity)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart or item not found")
        return cart
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}")
async def clear_cart(user_id: str):
    cart = await cart_service.clear_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return {"message": "Cart cleared successfully"}

@router.get("/{user_id}/items", response_model=List[CartItemResponse])
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
    return items 