import asyncio
from sqlalchemy import text
from database.db import async_session

async def test():
    async with async_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"Всего пользователей: {count}")

asyncio.run(test())

