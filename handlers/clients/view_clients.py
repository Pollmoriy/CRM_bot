# handlers/clients/view_clients.py
from loader import dp
from aiogram import types
from database.db import async_session
from database.models import Client
from sqlalchemy import select
from keyboards.clients_pages_kb import clients_pages_kb
import math

PAGE_SIZE = 5  # Количество клиентов на странице

def format_client_card(client: Client) -> str:
    """Возвращает красиво оформленный блок информации о клиенте"""
    return (
        f"👤 <b>{client.full_name}</b>\n"
        f"📞 Телефон: {client.phone or '-'}\n"
        f"💬 Telegram: {client.telegram or '-'}\n"
        f"🎂 Дата рождения: {client.birth_date.strftime('%Y-%m-%d') if client.birth_date else '-'}\n"
        f"🏷 Сегмент: {client.segment}\n"
        f"📝 Заметки: {client.notes or '-'}\n"
        f"──────────────"
    )

async def fetch_and_show_clients(callback: types.CallbackQuery, page: int = 1):
    """
    Показывает список клиентов постранично в виде красивых карточек
    """
    async with async_session() as session:
        result = await session.execute(select(Client).order_by(Client.added_date.desc()))
        clients = result.scalars().all()

    total_clients = len(clients)
    total_pages = max(1, math.ceil(total_clients / PAGE_SIZE))

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    clients_on_page = clients[start:end]

    if not clients_on_page:
        await callback.message.edit_text("Клиенты не найдены.")
        return

    # Формируем текст
    text = f"<b>Список клиентов — страница {page}/{total_pages}:</b>\n\n"
    for client in clients_on_page:
        text += format_client_card(client) + "\n"

    kb = clients_pages_kb(page, total_pages)
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except:
        await callback.message.answer(text, reply_markup=kb)
