# handlers/clients/delete_client.py
from aiogram import types
from loader import dp, safe_answer
from database.db import async_session
from database.models import Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5


async def show_delete_clients_page(callback: types.CallbackQuery, page: int = 1):
    offset_val = (page - 1) * PAGE_SIZE
    async with async_session() as session:
        result = await session.execute(select(Client).offset(offset_val).limit(PAGE_SIZE))
        clients = result.scalars().all()

    if not clients:
        await callback.message.answer("Список клиентов пуст.")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for client in clients:
        kb.add(
            InlineKeyboardButton(
                text=f"{client.full_name} ({client.phone or 'без телефона'}) ❌",
                callback_data=f"delete_{client.id_client}"
            )
        )

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"delete_page_{page-1}"))
    if len(clients) == PAGE_SIZE:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"delete_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_back"))

    await callback.message.edit_text("Выберите клиента для удаления:", reply_markup=kb)
    await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("delete_page_"))
async def delete_page_callback(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_delete_clients_page(callback, page)


@dp.callback_query_handler(lambda c: c.data.startswith("delete_") and not c.data.startswith("delete_page_"))
async def delete_client_callback(callback: types.CallbackQuery):
    client_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id_client == client_id))
        client = result.scalar_one_or_none()
        if client:
            await session.delete(client)
            await session.commit()
            await callback.answer(f"Клиент {client.full_name} успешно удалён.", show_alert=True)
        else:
            await callback.answer("Клиент не найден или уже удалён.", show_alert=True)

    await show_delete_clients_page(callback, page=1)
