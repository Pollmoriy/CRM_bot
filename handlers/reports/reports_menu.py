from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.dispatcher import Dispatcher
from sqlalchemy import select
from database.db import async_session_maker
from database.models import User
from keyboards.reports_kb import reports_menu_kb


async def reports_command_handler(message: types.Message):
    """Хендлер на кнопку '📊 Отчёты' в основном меню"""
    tg_id = str(message.from_user.id)

    async with async_session_maker() as session:
        # ORM-запрос через select()
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user_obj = result.scalar_one_or_none()

        if not user_obj:
            await message.answer("❌ Пользователь не найден в базе.")
            return

        # Получаем роль как str
        role = user_obj.role.value if user_obj.role else "employee"

        # InlineKeyboard для отчетов
        kb: InlineKeyboardMarkup = reports_menu_kb(role)

        await message.answer(
            "Выберите нужный отчёт:",
            reply_markup=kb
        )


def register_reports_menu(dp: Dispatcher):
    """Регистрация хендлера"""
    dp.register_message_handler(
        reports_command_handler,
        lambda msg: msg.text == "📊 Отчёты"
    )
