import asyncio
from functools import wraps
from typer import Typer
from db.postgres import async_session
from models.user import User
from models.role import Role
from models.user_role import UserRole
from core.config import settings

print("CLI started")

cli = Typer()


def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

async def get_or_create_role(session, role_name, description=None):
    result = await session.execute(
        Role.__table__.select().where(Role.name == role_name)
    )
    role_row = result.first()
    if role_row:
        role = await session.get(Role, role_row.id)
    else:
        role = Role(name=role_name, description=description)
        session.add(role)
        await session.commit()
        await session.refresh(role)
    return role

@cli.command()
@async_typer
async def create_superuser():
    print("Creating superuser...")
    async with async_session() as session:
        role = await get_or_create_role(session, 'super_admin', description='Super admin role')
        user = User(
            login=settings.SUPERUSER_LOGIN,
            password=settings.SUPERUSER_PASSWORD,
        )
        user.email = settings.SUPERUSER_EMAIL
        user.is_active = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
        session.add(UserRole(user_id=user.id, role_id=role.id))
        await session.commit()
        print(f"Superuser {user.login} created with role super_admin")

@cli.command()
@async_typer
async def create_admin(login: str, password: str, email: str):
    print("Creating admin user...")
    async with async_session() as session:
        role = await get_or_create_role(session, 'admin', description='Admin role')
        user = User(login=login, password=password)
        user.email = email
        user.is_active = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
        session.add(UserRole(user_id=user.id, role_id=role.id))
        await session.commit()
        print(f"User {login} created with role admin")

if __name__ == "__main__":
    cli()