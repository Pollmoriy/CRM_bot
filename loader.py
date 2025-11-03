# loader.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN

from database.db import engine, async_session, Base


# ⚙️ Создание экземпляров бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ⚙️ Инициализация базы данных
async def init_db():
    """
    Асинхронно создаёт таблицы, если их ещё нет.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных и таблицы готовы!")

