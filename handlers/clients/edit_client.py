# handlers/clients/edit_client.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loader import dp
from database.db import async_session
from database.models import Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5  # количество клиентов на одной странице

# Состояния для редактирования
class EditClientStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_new_value = State()
    waiting_for_client_selection = State()

# Показываем страницу клиентов для редактирования
async def show_edit_clients_page(callback: types.CallbackQuery, page: int = 1, search_name: str = ""):
    async with async_session() as session:
        query = select(Client)
        if search_name:
            query = query.where(Client.full_name.ilike(f"%{search_name}%"))
        result = await session.execute(query)
        clients = result.scalars().all()

    if not clients:
        await callback.message.answer("Список клиентов пуст.")
        return

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    clients_page = clients[start:end]

    kb = InlineKeyboardMarkup(row_width=1)
    for client in clients_page:
        kb.add(InlineKeyboardButton(
            text=f"{client.full_name} ({client.phone or 'без телефона'}) ✏️",
            callback_data=f"edit_{client.id_client}"
        ))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"edit_page_{page-1}"))
    if end < len(clients):
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"edit_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)

    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_back"))

    await callback.message.edit_text("Выберите клиента для редактирования:", reply_markup=kb)
    try:
        await callback.answer()
    except:
        pass

# Навигация по страницам
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("edit_page_"))
async def edit_page_callback(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_edit_clients_page(callback, page)

# Выбор клиента для редактирования
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("edit_") and not c.data.startswith("edit_page_"))
async def edit_client_selection(callback: types.CallbackQuery, state: FSMContext):
    client_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id_client == client_id))
        client = result.scalar_one_or_none()

    if not client:
        await callback.answer("Клиент не найден.", show_alert=True)
        return

    # Сохраняем ID клиента в состоянии
    await state.update_data(client_id=client.id_client)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Имя", callback_data="field_full_name"),
        InlineKeyboardButton("Телефон", callback_data="field_phone"),
        InlineKeyboardButton("Телеграм", callback_data="field_telegram"),
        InlineKeyboardButton("Дата рождения", callback_data="field_birth_date"),
        InlineKeyboardButton("Сегмент", callback_data="field_segment"),
        InlineKeyboardButton("Заметки", callback_data="field_notes"),
        InlineKeyboardButton("⬅️ Назад", callback_data="edit_page_1")
    )

    await callback.message.edit_text(f"Выберите поле для редактирования клиента {client.full_name}:", reply_markup=kb)
    await EditClientStates.waiting_for_field.set()
    try:
        await callback.answer()
    except:
        pass

# Выбор поля
@dp.callback_query_handler(lambda c: c.data.startswith("field_"), state=EditClientStates.waiting_for_field)
async def select_field_to_edit(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.replace("field_", "")
    await state.update_data(field=field)
    await EditClientStates.waiting_for_new_value.set()
    await callback.message.edit_text(f"Введите новое значение для поля '{field}':")
    try:
        await callback.answer()
    except:
        pass

# Ввод нового значения
@dp.message_handler(state=EditClientStates.waiting_for_new_value)
async def save_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    field = data.get("field")
    new_value = message.text

    if not client_id or not field:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.finish()
        return

    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id_client == client_id))
        client = result.scalar_one_or_none()
        if not client:
            await message.answer("Клиент не найден.")
            await state.finish()
            return

        # Обновляем только выбранное поле
        setattr(client, field, new_value)
        await session.commit()

    await message.answer(f"Поле '{field}' клиента '{client.full_name}' успешно обновлено.")
    await state.finish()
