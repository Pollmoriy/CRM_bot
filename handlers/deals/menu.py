from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select
from keyboards.deal_menu_kb import deal_menu_kb
from handlers.deals.add_deal import start_add_deal
from handlers.deals.edit_deal import show_edit_deals_page
from handlers.deals.delete_deal import show_delete_deals_page
from handlers.deals.view_deals import show_deals


@dp.message_handler(lambda m: m.text in ["💼 Сделки", "Мои сделки"])
async def open_deals_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"
    kb = deal_menu_kb(role)
    await message.answer("📁 Раздел 'Сделки'. Выберите действие:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    telegram_id = str(callback.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"

    if role == "admin":
        from keyboards.admin_kb import admin_menu as kb
    elif role == "manager":
        from keyboards.manager_kb import manager_menu as kb
    else:
        from keyboards.employee_kb import employee_menu as kb

    try:
        await callback.message.answer("🏠 Главное меню:", reply_markup=kb)
    except Exception:
        await callback.answer()
    else:
        await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("deal_"))
async def deal_main_callback(callback: types.CallbackQuery):
    action = callback.data

    if action == "deal_view":
        await show_deals(callback, page=1)
        return

    if action == "deal_add":
        await start_add_deal(callback)
        return

    if action == "deal_edit":
        await show_edit_deals_page(callback, page=1)
        return

    if action == "deal_delete":
        await show_delete_deals_page(callback, page=1)
        return

    await callback.answer("Функция пока не реализована.")

@dp.callback_query_handler(lambda c: c.data == "main_back")
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню (ReplyKeyboardMarkup)"""

    telegram_id = str(callback.from_user.id)

    # Получаем пользователя и его роль
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"

    # Подключаем нужную меню-клавиатуру
    if role == "admin":
        from keyboards.admin_kb import admin_menu as kb
    elif role == "manager":
        from keyboards.manager_kb import manager_menu as kb
    else:
        from keyboards.employee_kb import employee_menu as kb

    # Отправляем новое сообщение с Reply keyboard
    try:
        await callback.message.answer("🏠 Главное меню:", reply_markup=kb)
    except Exception:
        await callback.answer()
    else:
        await callback.answer()