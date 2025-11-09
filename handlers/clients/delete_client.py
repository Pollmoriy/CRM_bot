# handlers/clients/delete_client.py
from aiogram import types
from loader import dp
from database.db import async_session
from database.models import Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def start_delete_mode(callback: types.CallbackQuery):
    """Показывает список клиентов для удаления с inline кнопками."""
    async with async_session() as session:
        result = await session.execute(select(Client))
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

    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="client_back"))
    await callback.message.answer("Выберите клиента для удаления:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delete_"))
async def delete_client_callback(callback: types.CallbackQuery):
    client_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id_client == client_id))
        client = result.scalar_one_or_none()
        if client:
            await session.delete(client)
            await session.commit()
            await callback.message.edit_text(f"Клиент {client.full_name} успешно удалён.")
        else:
            await callback.message.edit_text("Клиент не найден или уже удалён.")

    # Скрытое подтверждение нажатия, чтобы не возникало ошибок
    try:
        await callback.answer(cache_time=1)
    except:
        pass
