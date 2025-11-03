# handlers/clients/menu.py
import asyncio
from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select

from keyboards.client_menu_kb import client_menu_kb

# ---------------------------
# Открытие меню Клиентов через кнопку или команду
# ---------------------------

async def get_user_role(telegram_id: str) -> str:
    """Получаем роль пользователя по telegram_id"""
    async with async_session() as session:
        result = await session.execute(
            select(User.role).where(User.telegram_id == telegram_id)
        )
        user_data = result.scalar_one_or_none()
        return user_data if user_data else "employee"


@dp.message_handler(lambda m: m.text in ["👥 Клиенты", "Клиенты"])
async def open_clients_from_main_menu(message: types.Message):
    role = await get_user_role(str(message.from_user.id))
    kb = client_menu_kb(role)
    await message.answer("Выберите действие с клиентами:", reply_markup=kb)


@dp.message_handler(commands=["clients", "clients_menu"])
async def open_clients_command(message: types.Message):
    await open_clients_from_main_menu(message)


# ---------------------------
# Обработчики inline callback'ов
# ---------------------------

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_callback_handler(callback: types.CallbackQuery):
    data = callback.data

    # ⚡ мгновенный ответ Telegram, чтобы убрать InvalidQueryID
    await callback.answer(cache_time=1)

    if data == "client_add":
        from handlers.clients.add_client import start_add_client
        await start_add_client(callback)
        return

    if data == "client_edit":
        await callback.message.answer("Выберите клиента для редактирования (введите имя или используйте поиск)...")
        return

    if data == "client_view":
        await callback.message.answer("Показываю список клиентов... (здесь будет пагинация и фильтры)")
        return

    if data == "client_delete":
        await callback.message.answer("Выберите клиента для удаления (подтверждение будет запрошено).")
        return

    if data == "client_back":
        await callback.message.answer("Возвращаю в главное меню.")
        return

