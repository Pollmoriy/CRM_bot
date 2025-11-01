# handlers/clients/menu.py
from aiogram import types
from loader import dp
from database.db import async_session
from database.models import User  # твоя модель пользователя
from sqlalchemy import select

from keyboards.client_menu_kb import client_menu_kb

# Если у тебя главная кнопка в ReplyKeyboard — перехватываем текст
@dp.message_handler(lambda m: m.text == "👥 Клиенты" or m.text == "Клиенты")
async def open_clients_from_main_menu(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

    # безопасный дефолт
    role = user.role.value if user and user.role else "employee"
    kb = client_menu_kb(role)
    await message.answer("Выберите действие с клиентами:", reply_markup=kb)


# Альтернатива: команда
@dp.message_handler(commands=["clients", "clients_menu"])
async def open_clients_command(message: types.Message):
    await open_clients_from_main_menu(message)


# Обработчики для Inline callback'ов — заглушки / роутеры
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("client_"))
async def client_callback_handler(callback: types.CallbackQuery):
    data = callback.data

    if data == "client_add":
        # Перенаправляем к хэндлеру добавления (в отдельном файле add_client.py)
        # Здесь можно вызвать стартовое сообщение или просто ответить и
        # ожидать следующего шага FSM, который реализован в add_client.py
        await callback.message.answer("Запуск процедуры добавления клиента...")
        # например: await start_add_client(callback.message) — реализовать в add_client.py
        await callback.answer()
        return

    if data == "client_edit":
        await callback.message.answer("Выберите клиента для редактирования (введите имя или используйте поиск)...")
        await callback.answer()
        return

    if data == "client_view":
        await callback.message.answer("Показываю список клиентов... (здесь будет пагинация и фильтры)")
        await callback.answer()
        return

    if data == "client_delete":
        await callback.message.answer("Выберите клиента для удаления (подтверждение будет запрошено).")
        await callback.answer()
        return

    if data == "client_back":
        # Возврат в главное меню: можно вызвать menu.show_main_menu или просто вывести текст
        await callback.message.answer("Возвращаю в главное меню.")
        await callback.answer()
        return
