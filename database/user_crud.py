from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import User, UserRole

# Получение пользователя по Telegram ID
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: str):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()

# Создание нового пользователя
async def create_user(session: AsyncSession, full_name: str, phone: str, telegram_id: str):
    # Проверяем, есть ли уже пользователи
    result = await session.execute(select(User))
    users = result.scalars().all()

    # Первый пользователь — Admin
    role = UserRole.admin if not users else UserRole.employee

    new_user = User(
        full_name=full_name,
        phone=phone,
        telegram_id=telegram_id,
        role=role
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

# Изменение роли пользователя (только для админа)
async def change_user_role(session: AsyncSession, user_id: int, new_role: UserRole):
    result = await session.execute(select(User).where(User.id_user == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.role = new_role
        await session.commit()
        await session.refresh(user)
        return user
    return None

# Привязка менеджера (manager_id)
async def assign_manager(session: AsyncSession, user_id: int, manager_id: int):
    result = await session.execute(select(User).where(User.id_user == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.manager_id = manager_id
        await session.commit()
        await session.refresh(user)
        return user
    return None
