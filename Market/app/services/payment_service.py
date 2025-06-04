from yookassa import Configuration, Payment
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    async def create_payment(self, amount: float, description: str, order_id: str):
        try:
            payment = Payment.create({
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"http://localhost:{settings.MARKET_PORT}/orders/{order_id}/success"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "order_id": order_id
                }
            })
            logger.info(f"Payment created for order {order_id}")
            return payment
        except Exception as e:
            logger.exception(f"Error creating payment for order {order_id}")
            raise

    async def get_payment_status(self, payment_id: str):
        try:
            payment = Payment.find_one(payment_id)
            logger.info(f"Retrieved payment status: {payment.status}")
            return payment.status
        except Exception as e:
            logger.exception(f"Error getting payment status for {payment_id}")
            raise

payment_service = PaymentService()
