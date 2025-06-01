from typing import Any, Callable
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.order_service import OrderService

import dependencies.services.auth_service_factory
import dependencies.services.role_service_factory
import dependencies.services.user_service_factory
import dependencies.services.token_storage_factory
import dependencies.services.user_role_service_factory
from dependencies.registrator import dependencies_container

def setup_dependencies(app: FastAPI, mapper: dict[Any, Callable] | None = None) -> None:
    """Настройка всех зависимостей приложения, включая MongoDB и контейнер зависимостей."""
    
    mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    db = mongo_client[settings.mongo_db_name]
    app.state.order_service = OrderService(db)
    
    if mapper is None:
        mapper = dependencies_container
        
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency
