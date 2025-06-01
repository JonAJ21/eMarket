import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Instrument HTTP metrics and mount Prometheus endpoint
instrumentator = Instrumentator()
instrumentator.add(metrics.default())
instrumentator.instrument(app)
app.mount("/metrics", make_asgi_app())

# In-memory storage with multiple performances
tickets = {
    "1": {"name": "Hamlet", "available": 20, "price": 50.0},
    "2": {"name": "King Lear", "available": 20, "price": 45.0},
    "3": {"name": "Macbeth", "available": 20, "price": 60.0},
    "4": {"name": "Othello", "available": 20, "price": 55.0},
}
bookings = {}

# Prometheus metrics
purchase_success_counter = Counter("ticket_purchase_success_total", "Total successful ticket purchases")
purchase_failure_counter = Counter("ticket_purchase_failure_total", "Total interrupted ticket purchases")
purchase_error_counter = Counter("ticket_purchase_errors_total", "Errors during ticket purchase", ["error"])
purchase_latency_histogram = Histogram("ticket_purchase_duration_seconds", "Duration of ticket purchase process")
# Gauges for current state
ticket_available_gauge = Gauge("ticket_available", "Number of available tickets", ["ticket_id"])
wallet_balance_gauge = Gauge("wallet_balance", "Balance of user wallet", ["card_number"])
active_bookings_gauge = Gauge("active_bookings", "Current number of active bookings")

# Initialize ticket gauges for all performances
for tid, info in tickets.items():
    ticket_available_gauge.labels(ticket_id=f'{tid} - {info["name"]}').set(info["available"])


class PaymentGatewayMock:
    def __init__(self):
        self.reserved = {}
        self.wallets = {}

        self._init_wallet()

    def _init_wallet(self):
        self.wallets = {
            '123456789': 500,
            '987654321': 500,
            '5555': 5000,
        }
        for card_number, balance in self.wallets.items():
            wallet_balance_gauge.labels(card_number=card_number).set(balance)

    def reserve_funds(self, card_number: str, amount: float):
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
        wallet_balance_gauge.labels(card_number=card_number).set(self.wallets[card_number])
        logger.info(f"Captured {amount} on card {card_number}, remaining balance {self.wallets[card_number]}")
        return True

    def refund_funds(self, card_number: str, amount: float):
        logger.info(f"Refunding {amount} to card {card_number}")
        self.wallets[card_number] = self.wallets.get(card_number, 0) + amount
        wallet_balance_gauge.labels(card_number=card_number).set(self.wallets[card_number])
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
    with purchase_latency_histogram.time():
        try:
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
            ticket_available_gauge.labels(ticket_id=f'{request.ticket_id} - {ticket["name"]}').set(ticket["available"])
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
            active_bookings_gauge.set(len(bookings))
            purchase_success_counter.inc()
            logger.info(f"Booking successful {booking_id}")
            return {"booking_id": booking_id, "status": "booked"}
        except HTTPException:
            purchase_failure_counter.inc()
            raise
        except Exception as e:
            purchase_failure_counter.inc()
            purchase_error_counter.labels(error=str(e)).inc()
            logger.error(f"Booking failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))


@app.post("/refund")
def refund_ticket(request: RefundRequest):
    booking = bookings.get(request.booking_id)
    if not booking:
        logger.error(f"Booking {request.booking_id} not found")
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking["card_number"] != request.card_number:
        logger.error(f"Card number mismatch for booking {request.booking_id}")
        raise HTTPException(status_code=400, detail="Card number does not match booking")

    try:
        logger.info(f"Processing refund for booking {request.booking_id}")
        tickets[booking["ticket_id"]]["available"] += booking["quantity"]
        ticket_available_gauge.labels(ticket_id=f'{booking["ticket_id"]} - {tickets[booking["ticket_id"]]["name"]}').set(tickets[booking["ticket_id"]]["available"])
        logger.info(f"Restored {booking['quantity']} tickets for {booking['ticket_id']}")

        payment_gateway.refund_funds(request.card_number, booking["amount"])
        del bookings[request.booking_id]
        active_bookings_gauge.set(len(bookings))
        logger.info(f"Refund successful for booking {request.booking_id}")
        return {"booking_id": request.booking_id, "status": "refunded"}
    except Exception as e:
        logger.error(f"Refund failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
