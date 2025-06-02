from typing import List, Optional
from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException

from app.models.order import OrderModel
from app.schemas.payment import (
    Order, OrderCreate, OrderUpdate, OrderStatus,
    PaymentOrderEvent, DeliveryMethod, DeliveryAddress
)
from app.services.payment_service import payment_service
from app.services.kafka_service import kafka_service
from app.schemas.cart import Cart


class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.order_model = OrderModel(db)

    async def create_order(
        self,
        user_id: UUID,
        cart: Cart,
        delivery_address: dict,
        delivery_method: DeliveryMethod
    ) -> Order:
        try:
            delivery_address_obj = DeliveryAddress(**delivery_address)

            order_create = OrderCreate(
                user_id=user_id,
                delivery_address=delivery_address_obj,
                delivery_method=delivery_method
            )
            order = await self.order_model.create(order_create)

            payment = await payment_service.create_payment(
                amount=cart.total_amount,
                description=f"Order #{order.id}",
                order_id=str(order.id)
            )

            order_update = OrderUpdate(
                payment_id=payment.id,
                payment_url=payment.confirmation.confirmation_url
            )
            return await self.order_model.update(str(order.id), order_update)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

    async def process_payment(self, payment_id: str) -> Optional[Order]:
        try:
            payment_status = await payment_service.get_payment_status(payment_id)

            order = await self.order_model.get_by_payment_id(payment_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if payment_status == "succeeded":
                order = await self.order_model.update_status(str(order.id), OrderStatus.PAID)

                event = PaymentOrderEvent(
                    id=uuid4(),
                    user_id=order.user_id,
                    order_id=UUID(str(order.id)),
                    order_status=OrderStatus.PAID.value,
                    products=order.items,
                    is_paid=True,
                    delivery_address=str(order.delivery_address),
                    delivery_method=order.delivery_method
                )

                sales_events = event.to_sales_events()
                for sales_event in sales_events:
                    await kafka_service.send_sales_event(sales_event.model_dump())

                order_event = event.to_order_event()
                await kafka_service.send_order_event(order_event.model_dump())

                return order

            return None

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process payment: {str(e)}")

    async def get_user_orders(self, user_id: UUID) -> List[Order]:
        try:
            return await self.order_model.get_by_user_id(str(user_id))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user orders: {str(e)}")

    async def get_order(self, order_id: str) -> Optional[Order]:
        try:
            order = await self.order_model.get_by_id(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            return order
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get order: {str(e)}")


order_service = OrderService(None)
