import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio.client import Redis
from prometheus_fastapi_instrumentator import Instrumentator
from metrics import update_total_users
from db.postgres import async_session

from dependencies.main import setup_dependencies
from db import redis
from core.config import settings
from api.v1.accounts import router as accounts_router
from api.v1.users import router as users_router
from api.v1.roles import router as roles_router
from api.v1.sellers import router as sellers_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        db=0,
    )
    yield
    await redis.redis.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Market",
        docs_url="/api/docs",
        description="Market API",
        lifespan=lifespan
    )
    
    app.include_router(accounts_router, prefix="/api/v1/accounts")
    app.include_router(users_router, prefix="/api/v1/users")
    app.include_router(roles_router, prefix="/api/v1/roles")
    app.include_router(sellers_router, prefix="/api/v1/markets")
    
    
    
    setup_dependencies(app)
    

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