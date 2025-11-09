from aiogram import types
from loader import dp
from database.db import async_session
from database.models import Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5  # Количество клиентов на одной странице

async def show_delete_clients_page(callback: types.CallbackQuery, page: int = 1):
    """Показывает страницу клиентов для удаления с пагинацией."""
    async with async_session() as session:
        result = await session.execute(select(Client))
        clients = result.scalars().all()

    if not clients:
        await callback.message.answer("Список клиентов пуст.")
        return

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    clients_page = clients[start:end]

    kb = InlineKeyboardMarkup(row_width=1)
    for client in clients_page:
        kb.add(
            InlineKeyboardButton(
                text=f"{client.full_name} ({client.phone or 'без телефона'}) ❌",
                callback_data=f"delete_{client.id_client}"
            )
        )

    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"delete_page_{page-1}"))
    if end < len(clients):
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"delete_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)

    # Главное меню клиентов
    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_back"))

    # Редактируем сообщение, если оно уже существует
    if callback.message:
        await callback.message.edit_text("Выберите клиента для удаления:", reply_markup=kb)
    else:
        await callback.message.answer("Выберите клиента для удаления:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delete_page_"))
async def delete_page_callback(callback: types.CallbackQuery):
    """Обработка кнопок навигации страниц."""
    page = int(callback.data.split("_")[2])
    await show_delete_clients_page(callback, page)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delete_") and not c.data.startswith("delete_page_"))
async def delete_client_callback(callback: types.CallbackQuery):
    """Обработка удаления клиента."""
    client_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id_client == client_id))
        client = result.scalar_one_or_none()
        if client:
            await session.delete(client)
            await session.commit()
            # Подтверждение удаления через всплывающее окно
            await callback.answer(f"Клиент {client.full_name} успешно удалён.", show_alert=True)
        else:
            await callback.answer("Клиент не найден или уже удалён.", show_alert=True)

    # После удаления показываем ту же страницу заново (начинаем с первой)
    await show_delete_clients_page(callback, page=1)
