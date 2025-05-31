import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from redis.asyncio.client import Redis

from services.pubsub import RedisPubSub
from dependencies.main import setup_dependencies
from db import redis
from core.config import settings
from api.v1.accounts import router as accounts_router
from api.v1.users import router as users_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        db=0,
    )
    
    pubsub = RedisPubSub(client=redis.redis)
    
    async def message_handler(channel: str, message: Any):
        print(f"Received message on channel {channel}: {message}")
    
    async def background_subscriber():
        await pubsub.subscribe(channel="notifications", callback=message_handler)
    
    asyncio.create_task(background_subscriber())
    
    yield
    await pubsub.close()
    await redis.redis.aclose()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Market",
        docs_url="/api/docs",
        description="Market API",
        lifespan=lifespan
    )
    
    app.include_router(accounts_router, prefix="/accounts")
    app.include_router(users_router, prefix="/users")
    
    
    setup_dependencies(app)
    return app