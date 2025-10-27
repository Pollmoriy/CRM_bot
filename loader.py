import asyncio
from aiogram import Bot, Dispatcher
from database.db import engine, async_session, Base
from database.models import User
from config import BOT_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Создание экземпляров бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных и таблицы готовы!")

