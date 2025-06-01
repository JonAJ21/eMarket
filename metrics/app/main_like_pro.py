import logging
import functools
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
    "1": {"name": "Hamlet", "available": 50, "price": 50.0},
    "2": {"name": "King Lear", "available": 50, "price": 45.0},
    "3": {"name": "Macbeth", "available": 50, "price": 60.0},
    "4": {"name": "Othello", "available": 50, "price": 55.0},
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

# Initialize ticket gauges
for tid, info in tickets.items():
    ticket_available_gauge.labels(ticket_id=f'{tid} - {info["name"]}').set(info["available"])

# Decorators for metrics


def purchase_metrics(func):
    @functools.wraps(func)
    async def wrapper(request):
        with purchase_latency_histogram.time():
            try:
                result = await func(request)
                purchase_success_counter.inc()
                return result
            except HTTPException:
                purchase_failure_counter.inc()
                raise
            except Exception as e:
                purchase_failure_counter.inc()
                purchase_error_counter.labels(error=str(e)).inc()
                raise

    return wrapper


def ticket_metrics(func):
    @functools.wraps(func)
    async def wrapper(request):
        result = await func(request)
        ticket_available_gauge.labels(ticket_id=f'{request.ticket_id} - {tickets[request.ticket_id]["name"]}').set(tickets[request.ticket_id]["available"])
        return result

    return wrapper


def active_bookings_metrics(func):
    @functools.wraps(func)
    async def wrapper(request):
        result = await func(request)
        active_bookings_gauge.set(len(bookings))
        return result

    return wrapper


def refund_metrics(func):
    @functools.wraps(func)
    async def wrapper(request):
        booking_info = bookings.get(request.booking_id)
        result = await func(request)
        if booking_info:
            ticket_available_gauge.labels(ticket_id=f'{booking_info["ticket_id"]} - {tickets[booking_info["ticket_id"]]["name"]}').set(
                tickets[booking_info["ticket_id"]]["available"]
            )
            active_bookings_gauge.set(len(bookings))
        return result

    return wrapper


# Mock payment gateway with wallet metrics decorator
def wallet_metrics(func):
    @functools.wraps(func)
    def wrapper(self, card_number: str, amount: float):
        result = func(self, card_number, amount)
        wallet_balance_gauge.labels(card_number=card_number).set(self.wallets.get(card_number, 0))
        return result

    return wrapper


class PaymentGatewayMock:
    def __init__(self):
        self.reserved = {}
        self.wallets = {}

        for card_number in ["1234", "4444", "1342", "5555"]:
            self._init_wallet(card_number, 500)

    @wallet_metrics
    def _init_wallet(self, card_number: str, amount: float):
        self.wallets[card_number] = amount

    @wallet_metrics
    def reserve_funds(self, card_number: str, amount: float):
        if card_number not in self.wallets:
            self.wallets[card_number] = 500
        if self.wallets[card_number] < amount:
            raise Exception("Insufficient funds in wallet")
        self.reserved[card_number] = self.reserved.get(card_number, 0) + amount

    @wallet_metrics
    def capture_funds(self, card_number: str, amount: float):
        reserved_amount = self.reserved.get(card_number, 0)
        if reserved_amount < amount:
            raise Exception("Insufficient reserved funds")
        self.reserved[card_number] -= amount
        self.wallets[card_number] -= amount

    @wallet_metrics
    def refund_funds(self, card_number: str, amount: float):
        self.wallets[card_number] = self.wallets.get(card_number, 0) + amount


payment_gateway = PaymentGatewayMock()


# Request models
class BookingRequest(BaseModel):
    user_id: str
    ticket_id: str
    quantity: int
    card_number: str


class RefundRequest(BaseModel):
    booking_id: str
    card_number: str


# Endpoints
@app.post("/book")
@purchase_metrics
@ticket_metrics
@active_bookings_metrics
async def book_ticket(request: BookingRequest):
    ticket = tickets.get(request.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket["available"] < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")

    amount = ticket["price"] * request.quantity
    ticket["available"] -= request.quantity
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
    return {"booking_id": booking_id, "status": "booked"}


@app.post("/refund")
@refund_metrics
async def refund_ticket(request: RefundRequest):
    booking = bookings.get(request.booking_id)
    if not booking or booking["card_number"] != request.card_number:
        raise HTTPException(status_code=400, detail="Invalid refund request")
    tickets[booking["ticket_id"]]["available"] += booking["quantity"]
    payment_gateway.refund_funds(request.card_number, booking["amount"])
    del bookings[request.booking_id]
    return {"booking_id": request.booking_id, "status": "refunded"}


@app.get("/bookings/{user_id}")
async def get_user_bookings(user_id: str):
    user_bookings = [
        {"booking_id": bid, "ticket_id": info["ticket_id"], "quantity": info["quantity"], "amount": info["amount"]}
        for bid, info in bookings.items()
        if info.get("user_id") == user_id
    ]
    return {"user_id": user_id, "bookings": user_bookings}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
