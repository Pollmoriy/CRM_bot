# database/db.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

# 🚀 Формируем URL (MySQL через asyncmy)
DATABASE_URL = (
    f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ⚙️ Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"connect_timeout": 30},
    future=True,
)

# ⚙️ Создаём фабрику асинхронных сессий
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ❗ ВАЖНО — алиас для совместимости:
# Теперь можно писать: async with async_session() as session:
async_session = async_session_maker

# 📘 Декларативная база моделей
Base = declarative_base()

# 🧩 Контекстный менеджер для замера времени SQL
async def timed_session():
    import time
    async with async_session() as session:
        start = time.perf_counter()
        yield session
        duration = time.perf_counter() - start
        print(f"⏱ SQL-запрос выполнен за {duration:.3f} сек")

