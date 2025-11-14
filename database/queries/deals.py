from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models import Deal, Client, User
from database.db import async_session_maker


async def get_deals(page: int = 1, per_page: int = 5):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal)
            .options(
                selectinload(Deal.client),
                selectinload(Deal.manager)
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return result.scalars().all()


async def get_deal_by_id(deal_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal)
            .options(
                selectinload(Deal.client),
                selectinload(Deal.manager),
                selectinload(Deal.tasks)
            )
            .where(Deal.id == deal_id)
        )
        return result.scalar_one_or_none()
