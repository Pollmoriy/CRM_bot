from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User
from sqlalchemy import select
from keyboards.client_menu_kb import client_menu_kb
from keyboards.clients_pages_kb import top_clients_kb, filter_options_kb
from handlers.clients.view_clients import show_clients_page
from handlers.clients.search_client import start_search_client

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


# CALLBACKS: обработка кнопок меню клиентов
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_main_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    data = callback.data

    # Просмотр списка
    if data in ("client_view", "view_clients"):
        await show_clients_page(callback.message, page=1, search_name="", filter_by="")
        return

    # Поиск
    if data in ("client_search", "search_client"):
        await start_search_client(callback)
        return

    # Фильтр — показываем варианты фильтрации
    if data == "client_filter":
        await callback.message.edit_reply_markup(reply_markup=filter_options_kb())
        return

    # Добавить
    if data == "client_add":
        from handlers.clients.add_client import start_add_client
        await start_add_client(callback)
        return

    # Редактировать / Удалить
    if data in ("client_edit", "client_delete"):
        await callback.message.answer(
            "Выберите клиента из списка (Просмотр списка → нажмите на карточку клиента)."
        )
        return

    # Назад в главное меню
    if data == "client_back":
        from handlers.menu import show_main_menu
        await show_main_menu(callback.message)


# Обработка выбора фильтра
@dp.callback_query_handler(lambda c: c.data.startswith("filter|"))
async def filter_clients_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    filter_by = callback.data.split("|")[1]
    filter_by = "" if filter_by == "none" else filter_by
    await show_clients_page(callback.message, page=1, search_name="", filter_by=filter_by)
