# handlers/clients/menu.py
from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select

from keyboards.client_menu_kb import client_menu_kb
from keyboards.clients_pages_kb import top_clients_kb
from handlers.clients.view_clients import show_clients_page
from handlers.clients.search_client import start_search_client

# Импортируем обработчики фильтра
from handlers.clients.filter_clients import register_filter_clients
register_filter_clients(dp)  # <-- регистрация кнопки "Фильтр"

# Открыть меню клиентов из основного ReplyKeyboard
@dp.message_handler(lambda m: m.text in ["👥 Клиенты", "Клиенты"])
async def open_clients_from_main_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role if user and user.role else None
    kb = client_menu_kb(role.value if role else "employee")
    await message.answer("Выберите действие с клиентами:", reply_markup=kb)

# Команда
@dp.message_handler(commands=["clients", "clients_menu"])
async def open_clients_command(message: types.Message):
    await open_clients_from_main_menu(message)

# Основные кнопки меню клиентов
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_main_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    data = callback.data

    if data in ("client_view", "view_clients"):
        await show_clients_page(callback.message, page=1, search_name="", filter_by="")
        return

    if data in ("client_search", "search_client"):
        await start_search_client(callback)
        return

    if data == "client_add":
        from handlers.clients.add_client import start_add_client
        await start_add_client(callback)
        return

    if data in ("client_edit", "client_delete"):
        await callback.message.answer("Выберите клиента из списка (Просмотр списка → нажмите на карточку клиента).")
        return

    if data == "client_back":
        # возвращаемся к полному списку клиентов
        await show_clients_page(callback.message, page=1, search_name="", filter_by="")
        return
