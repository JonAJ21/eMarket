import asyncio
from functools import wraps
from typer import Typer
from db.postgres import get_session
from services.role import BaseRoleService
from dependencies.services.role_service_factory import create_role_service
from schemas.role import Roles
from schemas.role import RoleCreateDTO

import models.role
import models.seller_info
import models.social_account
import models.user_history
import models.user
import models.user_role

cli = Typer()

def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

@cli.command()
@async_typer
async def init_roles():
    roles = [role.value for role in Roles.__members__.values()]
    try:
        async with get_session() as session:
            role_service: BaseRoleService = create_role_service(session=session)
            for role in roles:
                dto: RoleCreateDTO = RoleCreateDTO(
                    name=role,
                    description=f"{role}"
                )
                
                role = await role_service.create_role(dto=dto)
                print(f"Role {role.name} created with ID {role.id}")
    except Exception as e:
        print(f"Error creating roles: {e}")

      
   

@cli.command()
@async_typer
async def create_superuser():
    ...
    

cli()