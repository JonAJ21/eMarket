from typing import Any, Callable
from fastapi import FastAPI

import dependencies.services.auth_service_factory
import dependencies.services.role_service_factory
import dependencies.services.user_service_factory
import dependencies.services.token_storage_factory
import dependencies.services.user_role_service_factory

from dependencies.registrator import dependencies_container

def setup_dependencies(app: FastAPI, mapper: dict[Any, Callable] | None = None) -> None:
    if mapper is None:
        mapper = dependencies_container
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency