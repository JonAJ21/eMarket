from prometheus_client import Gauge
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.user import User

total_users_gauge = Gauge('total_users', 'Current total number of users')

async def update_total_users(session: AsyncSession):
    result = await session.execute(select(func.count()).select_from(User))
    count = result.scalar()
    total_users_gauge.set(count) 