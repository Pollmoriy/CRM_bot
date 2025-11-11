from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select
from keyboards.deal_menu_kb import deal_menu_kb
from handlers.deals.add_deal import start_add_deal

# Главное меню в зависимости от роли
ROLE_MENUS = {
    "admin": "admin_menu",      # эти переменные должны импортироваться из соответствующих файлов
    "manager": "manager_menu",
    "employee": "employee_menu"
}


@dp.message_handler(lambda m: m.text in ["💼 Сделки", "Мои сделки"])
async def open_deals_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"
    kb = deal_menu_kb(role)  # всегда InlineKeyboardMarkup
    await message.answer("📁 Раздел 'Сделки'. Выберите действие:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    telegram_id = str(callback.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"

    # Получаем клавиатуру в зависимости от роли
    if role == "admin":
        from keyboards.admin_kb import admin_menu
        kb = admin_menu
    elif role == "manager":
        from keyboards.manager_kb import manager_menu
        kb = manager_menu
    else:
        from keyboards.employee_kb import employee_menu
        kb = employee_menu

    # Всегда передаем InlineKeyboardMarkup или None
    kb = kb if isinstance(kb, types.InlineKeyboardMarkup) else None

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("deal_"))
async def deal_main_callback(callback: types.CallbackQuery):
    data = callback.data

    if data == "deal_view":
        # показать список сделок
        ...
    elif data == "deal_edit":
        # редактирование
        ...
    elif data == "deal_add":
        await start_add_deal(callback)
