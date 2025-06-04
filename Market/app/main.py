import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio.client import Redis

from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from db.mongodb import MongoDB

from prometheus_fastapi_instrumentator import Instrumentator
from metrics import update_total_users
from db.postgres import async_session

from dependencies.main import setup_dependencies
from db import redis
from core.config import settings
from api.v1.accounts import router as accounts_router
from api.v1.users import router as users_router

from api.v1 import products, categories, reviews, cart
from metrics.middleware import PrometheusMiddleware
from metrics.decorators import product_rating
from services.review_service import ReviewService

from api.v1.roles import router as roles_router
from api.v1.sellers import router as sellers_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    await MongoDB.connect_to_database()
    
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        db=0,
    )
    yield
    await redis.redis.close()
    await MongoDB.close_database_connection()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Market",
        docs_url="/api/docs",
        description="Market API",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(accounts_router, prefix="/accounts")
    app.include_router(users_router, prefix="/users")
    app.include_router(roles_router, prefix="/roles")
    app.include_router(sellers_router, prefix="/markets")
    
    app.add_middleware(PrometheusMiddleware)
    
    async def init_product_ratings():
        review_service = ReviewService()
        products = await review_service.product_repo.get_all()
        for product in products:
            rating = await review_service.get_product_rating(str(product.id))
            product_rating.labels(product_id=str(product.id)).set(rating)
    
 
    app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
    app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
    app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
    app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
    

    setup_dependencies(app)

    # Добавляем эндпоинт для метрик Prometheus
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Инициализируем метрики при старте
    @app.on_event("startup")
    async def startup_event():
        await init_product_ratings()

    @app.get("/")
    async def root():
        return {"message": "Welcome to eMarket API"}


    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    async def periodic_user_count_update():
        while True:
            async with async_session() as session:
                await update_total_users(session)
            await asyncio.sleep(30)

    @app.on_event("startup")
    async def start_metrics_updater():

        asyncio.create_task(periodic_user_count_update())

    
    return app