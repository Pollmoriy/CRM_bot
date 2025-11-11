# loader.py
import time
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import InvalidQueryID, MessageNotModified
from config import BOT_TOKEN
from database.db import engine, Base


# ⚙️ Создание экземпляров бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode="HTML", timeout=30)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ⚙️ Инициализация базы данных
async def init_db():
    """
    Асинхронно создаёт таблицы, если их ещё нет.
    """
    start = time.perf_counter()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    duration = time.perf_counter() - start
    print(f"✅ База данных готова! (инициализация заняла {duration:.2f} сек)")


# ⚙️ Глобальный обработчик ошибок (чтобы не ронять бота)
@dp.errors_handler()
async def global_error_handler(update, exception):
    """
    Перехватывает и игнорирует неопасные ошибки Telegram, логирует остальные.
    """
    if isinstance(exception, (InvalidQueryID, MessageNotModified)):
        return True  # игнорируем
    print(f"⚠️ Ошибка: {exception}")
    return True


# ⚙️ Безопасный ответ на callback_query (встроим в каждый хендлер)
async def safe_answer(callback_query: types.CallbackQuery):
    try:
        await callback_query.answer()
    except (InvalidQueryID, MessageNotModified):
        pass
    except Exception as e:
        print(f"⚠️ Ошибка callback.answer(): {e}")


# ⚙️ Декоратор для замера скорости выполнения функций
def measure_time(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"⏱ {func.__name__} выполнен за {duration:.2f} сек")
        return result
    return wrapper
