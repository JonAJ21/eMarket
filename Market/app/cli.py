import asyncio
from functools import wraps
from typer import Typer
import uvicorn

cli = Typer()


def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

@cli.command()
@async_typer
async def create_superuser():
    ...