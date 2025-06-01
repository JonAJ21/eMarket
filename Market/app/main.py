import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio.client import Redis
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from db.mongodb import MongoDB
from dependencies.main import setup_dependencies
from db import redis
from core.config import settings
from api.v1.accounts import router as accounts_router
from api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Инициализируем MongoDB перед всем остальным
    await MongoDB.connect_to_database()
    
    # Инициализируем Redis
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
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(accounts_router, prefix="/accounts")
    app.include_router(users_router, prefix="/users")
    
    # Импортируем роутеры здесь, после инициализации MongoDB
    from api.v1 import products, categories, reviews, cart
    
    # Подключение роутеров
    app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
    app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
    app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
    app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
    
    setup_dependencies(app)

    # Добавляем эндпоинт для метрик Prometheus
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    @app.get("/")
    async def root():
        return {"message": "Welcome to eMarket API"}
    
    return app