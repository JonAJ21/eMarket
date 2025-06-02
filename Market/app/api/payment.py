from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from app.schemas.payment import Order, OrderCreate, DeliveryAddress, DeliveryMethod
from app.services.order_service import order_service
from app.core.auth import get_current_user
from app.schemas.user import User
from app.utils.stubs import get_cart_stub

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=Order)
async def create_order(
    delivery_address: DeliveryAddress,
    delivery_method: DeliveryMethod,
    current_user: User = Depends(get_current_user)
):
    cart = get_cart_stub(str(current_user.id))
    order = await order_service.create_order(
        user_id=current_user.id,
        cart=cart,
        delivery_address=delivery_address,
        delivery_method=delivery_method
    )
    return order

@router.get("/", response_model=List[Order])
async def get_user_orders(current_user: User = Depends(get_current_user)):
    return await order_service.get_user_orders(current_user.id)

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    order = await order_service.get_order(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/webhook/yookassa")
async def yookassa_webhook(payment_data: dict):
    payment_id = payment_data.get("object", {}).get("id")
    if not payment_id:
        raise HTTPException(status_code=400, detail="Invalid payment data")

    order = await order_service.process_payment(payment_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"status": "success"}
