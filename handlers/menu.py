from database.user_crud import get_user_by_telegram_id
from database.models import UserRole
from database.db import async_session
from loader import dp

@dp.message_handler(commands=["menu"])
async def main_menu(message):
    async with async_session() as session:
        user = await get_user_by_telegram_id(session, str(message.from_user.id))
        if not user:
            await message.answer("Сначала зарегистрируйтесь через /start")
            return

        if user.role == UserRole.admin:
            await message.answer("Добро пожаловать, Админ! Здесь панель администратора.")
        elif user.role == UserRole.manager:
            await message.answer("Добро пожаловать, Менеджер! Здесь ваше меню.")
        else:
            await message.answer("Добро пожаловать, Сотрудник! Здесь ваше меню.")
