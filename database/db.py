from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

# Подключение к существующей БД
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)

# Фабрика сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Базовый класс моделей
Base = declarative_base()
