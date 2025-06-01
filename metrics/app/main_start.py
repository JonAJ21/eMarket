import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# In-memory storage with multiple performances
tickets = {
    "1": {"name": "Hamlet", "available": 10, "price": 50.0},
    "2": {"name": "King Lear", "available": 8, "price": 45.0},
    "3": {"name": "Macbeth", "available": 5, "price": 60.0},
    "4": {"name": "Othello", "available": 7, "price": 55.0},
}
bookings = {}


class PaymentGatewayMock:
    def __init__(self):
        self.reserved = {}
        self.wallets = {}

    def reserve_funds(self, card_number: str, amount: float):
        if card_number not in self.wallets:
            balance = 500
            self.wallets[card_number] = balance
            logger.info(f"Initialized wallet for {card_number} with balance {balance}")
        logger.info(f"Attempting to reserve {amount} on card {card_number}")
        if self.wallets[card_number] < amount:
            raise Exception("Insufficient funds in wallet")
        self.reserved[card_number] = self.reserved.get(card_number, 0) + amount
        logger.info(f"Reserved {amount} on card {card_number}, total reserved {self.reserved[card_number]}")
        return True

    def capture_funds(self, card_number: str, amount: float):
        logger.info(f"Capturing {amount} on card {card_number}")
        reserved_amount = self.reserved.get(card_number, 0)
        if reserved_amount < amount:
            raise Exception("Insufficient reserved funds")
        self.reserved[card_number] -= amount
        self.wallets[card_number] -= amount
        logger.info(f"Captured {amount} on card {card_number}, remaining balance {self.wallets[card_number]}")
        return True

    def refund_funds(self, card_number: str, amount: float):
        logger.info(f"Refunding {amount} to card {card_number}")
        self.wallets[card_number] = self.wallets.get(card_number, 0) + amount
        logger.info(f"Refunded {amount} to card {card_number}, new balance {self.wallets[card_number]}")
        return True


payment_gateway = PaymentGatewayMock()


class BookingRequest(BaseModel):
    user_id: str
    ticket_id: str
    quantity: int
    card_number: str


class RefundRequest(BaseModel):
    booking_id: str
    card_number: str


@app.post("/book")
def book_ticket(request: BookingRequest):
    ticket = tickets.get(request.ticket_id)
    if not ticket:
        logger.error(f"Ticket {request.ticket_id} not found")
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket["available"] < request.quantity:
        logger.error(f"Not enough tickets available for {request.ticket_id}")
        raise HTTPException(status_code=400, detail="Not enough tickets available")

    amount = ticket["price"] * request.quantity
    logger.info(f"Booking {request.quantity} of ticket {request.ticket_id} for user {request.user_id}")
    ticket["available"] -= request.quantity
    logger.info(f"Reserved {request.quantity} tickets, remaining {ticket['available']}")

    payment_gateway.reserve_funds(request.card_number, amount)
    payment_gateway.capture_funds(request.card_number, amount)

    booking_id = str(len(bookings) + 1)
    bookings[booking_id] = {
        "user_id": request.user_id,
        "ticket_id": request.ticket_id,
        "quantity": request.quantity,
        "amount": amount,
        "card_number": request.card_number,
    }
    logger.info(f"Booking successful {booking_id}")
    return {"booking_id": booking_id, "status": "booked"}


@app.post("/refund")
def refund_ticket(request: RefundRequest):
    booking = bookings.get(request.booking_id)
    if not booking:
        logger.error(f"Booking {request.booking_id} not found")
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking["card_number"] != request.card_number:
        logger.error(f"Card number mismatch for booking {request.booking_id}")
        raise HTTPException(status_code=400, detail="Card number does not match booking")

    logger.info(f"Processing refund for booking {request.booking_id}")
    tickets[booking["ticket_id"]]["available"] += booking["quantity"]
    logger.info(f"Restored {booking['quantity']} tickets for {booking['ticket_id']}")

    payment_gateway.refund_funds(request.card_number, booking["amount"])
    del bookings[request.booking_id]
    logger.info(f"Refund successful for booking {request.booking_id}")
    return {"booking_id": request.booking_id, "status": "refunded"}


@app.get("/bookings/{user_id}")
def get_user_bookings(user_id: str):
    user_bookings = []
    for bid, info in bookings.items():
        if info.get("user_id") == user_id:
            entry = {
                "booking_id": bid,
                "ticket_id": info["ticket_id"],
                "quantity": info["quantity"],
                "amount": info["amount"],
            }
            user_bookings.append(entry)
    logger.info(f"Fetched {len(user_bookings)} bookings for user {user_id}")
    return {"user_id": user_id, "bookings": user_bookings}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
