from aiogram import types
from loader import dp, safe_answer
from sqlalchemy import select
from database.db import async_session
from database.models import User
from keyboards.deal_menu_kb import deal_menu_kb
from handlers.deals.view_deals import show_deals
from handlers.deals.filter_deals import start_filter_deal, register_filter_deals
from handlers.deals.add_deal import start_add_deal
from handlers.deals.edit_deal import show_edit_deals_page
from handlers.deals.delete_deal import show_delete_deals_page
from handlers.deals.search_deals import start_search_deal

# ------------------------------
# Главное меню сделок в зависимости от роли
# ------------------------------
async def get_main_menu_kb(user: User):
    role = user.role.value if user and user.role else "employee"
    return deal_menu_kb(role)

# ------------------------------
# Открытие меню сделок
# ------------------------------
@dp.message_handler(lambda m: m.text in ["💼 Сделки", "💼 Мои сделки"])
async def open_deals_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    kb = deal_menu_kb(user.role.value if user else "employee")
    await message.answer("📁 Раздел 'Сделки'. Выберите действие:", reply_markup=kb)

# ------------------------------
# Callback главного меню
# ------------------------------
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("deal_"))
async def deal_main_callback(callback: types.CallbackQuery):
    await safe_answer(callback)
    action = callback.data

    if action == "deal_view":
        await show_deals(callback, page=1, search_name="", filter_by="")
    elif action == "deal_add":
        await start_add_deal(callback)
    elif action == "deal_edit":
        await show_edit_deals_page(callback, page=1)
    elif action == "deal_delete":
        await show_delete_deals_page(callback, page=1)
    elif action == "deal_search":
        await start_search_deal(callback)
    elif action == "deal_filter":
        await start_filter_deal(callback)
    elif action == "deal_back":
        telegram_id = str(callback.from_user.id)
        async with async_session() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
        kb = await get_main_menu_kb(user)
        await callback.message.edit_text("📁 Раздел 'Сделки'. Выберите действие:", reply_markup=kb)
    else:
        await callback.answer("Функция пока не реализована.")

# ------------------------------
# Регистрируем фильтры
# ------------------------------
try:
    register_filter_deals(dp)
except Exception:
    pass
