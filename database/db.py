# database/db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


# 🚀 Формируем URL (MySQL через asyncmy)
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ⚙️ Асинхронный движок (ускорено + безопасный таймаут)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,       # проверка соединения перед каждым запросом
    pool_recycle=1800,        # пересоздание соединения каждые 30 мин
    connect_args={"connect_timeout": 30},  # увеличиваем время на коннект
    future=True
)

# ⚙️ Фабрика асинхронных сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 📘 Базовый класс для моделей
Base = declarative_base()


# 🧩 Утилита для отладки: замер времени SQL-запросов
async def timed_session():
    """
    Контекстный менеджер, который измеряет время выполнения блока кода.
    Используй для отладки медленных мест.
    """
    import time
    async with async_session() as session:
        start = time.perf_counter()
        yield session
        duration = time.perf_counter() - start
        print(f"⏱ SQL-запрос выполнен за {duration:.3f} сек")
