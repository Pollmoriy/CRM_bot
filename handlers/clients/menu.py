from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select

from keyboards.client_menu_kb import client_menu_kb
from handlers.clients.view_clients import show_clients_page
from handlers.clients.add_client import start_add_client
from handlers.clients.delete_client import start_delete_mode
from handlers.clients.search_client import start_search_client
from handlers.clients.filter_clients import register_filter_clients

# Регистрация фильтров
register_filter_clients(dp)

@dp.message_handler(lambda m: m.text in ["👥 Клиенты", "Клиенты"])
async def open_clients_from_main_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"
    kb = client_menu_kb(role)
    await message.answer("Выберите действие с клиентами:", reply_markup=kb)


@dp.message_handler(commands=["clients", "clients_menu"])
async def open_clients_command(message: types.Message):
    await open_clients_from_main_menu(message)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_main_callback(callback: types.CallbackQuery):
    data = callback.data
    # быстрое скрытое подтверждение нажатия
    try:
        await callback.answer(cache_time=1)
    except:
        pass

    if data in ("client_view", "view_clients"):
        await show_clients_page(callback.message, page=1, search_name="", filter_by="")
    elif data in ("client_search", "search_client"):
        await start_search_client(callback)
    elif data == "client_add":
        await start_add_client(callback)
    elif data in ("client_edit", "client_delete"):
        # Запуск режима удаления клиентов
        await start_delete_mode(callback)
    elif data == "client_back":
        await show_clients_page(callback.message, page=1, search_name="", filter_by="")
