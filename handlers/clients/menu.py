from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select
from keyboards.client_menu_kb import client_menu_kb
from handlers.clients.view_clients import fetch_and_show_clients

# Главное меню Клиентов
@dp.message_handler(lambda m: m.text in ["👥 Клиенты", "Клиенты"])
async def open_clients_from_main_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    role = user.role.value if user and user.role else "employee"
    kb = client_menu_kb(role)
    await message.answer("Выберите действие с клиентами:", reply_markup=kb)

# Команда альтернативно
@dp.message_handler(commands=["clients", "clients_menu"])
async def open_clients_command(message: types.Message):
    await open_clients_from_main_menu(message)

# Кнопка "Просмотр списка"
@dp.callback_query_handler(lambda c: c.data == "view_clients")
async def show_clients(callback: types.CallbackQuery):
    await fetch_and_show_clients(callback, page=1)
    await callback.answer(cache_time=1)

# Пагинация
@dp.callback_query_handler(lambda c: c.data.startswith("clients_page:"))
async def change_clients_page(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[1])
    await fetch_and_show_clients(callback, page=page)
    await callback.answer(cache_time=1)

# Остальные кнопки клиента
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_callback_handler(callback: types.CallbackQuery):
    data = callback.data

    if data == "client_add":
        from handlers.clients.add_client import start_add_client
        await start_add_client(callback)
        await callback.answer()
        return

    if data == "client_edit":
        await callback.message.answer("Выберите клиента для редактирования...")
        await callback.answer()
        return

    if data == "client_delete":
        await callback.message.answer("Выберите клиента для удаления...")
        await callback.answer()
        return
