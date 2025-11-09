# handlers/clients/view_clients.py
from aiogram import types
from sqlalchemy import text
from database.db import async_session
from loader import dp
from keyboards.clients_pages_kb import top_clients_kb, clients_nav_kb, filter_values_kb
from datetime import datetime, timedelta

PAGE_SIZE = 5

def format_client_card_row(row) -> str:
    full_name = getattr(row, "full_name", row[1])
    phone = getattr(row, "phone", "-") or "-"
    telegram = getattr(row, "telegram", "-") or "-"
    birth = getattr(row, "birth_date", None)
    birth_str = birth.strftime('%Y-%m-%d') if birth else "-"
    segment = getattr(row, "segment", "-") or "-"
    notes = getattr(row, "notes", "-") or "-"
    return (
        f"👤 <b>{full_name}</b>\n"
        f"📞 <b>{phone}</b>\n"
        f"💬 <b>{telegram}</b>\n"
        f"🎂 <b>{birth_str}</b>\n"
        f"🏷 <b>{segment}</b>\n"
        f"📝 <b>{notes}</b>\n"
        f"─────────────────────────────\n"
    )


async def _call_get_clients(session, search_name: str, filter_by: str, page: int, page_size: int):
    filter_type, filter_value = "", ""
    if filter_by and "|" in filter_by:
        filter_type, filter_value = filter_by.split("|", 1)

    offset_val = (page - 1) * page_size

    if filter_type == "segment":
        stmt = text("""
            SELECT * FROM clients
            WHERE full_name LIKE :search AND segment = :value
            ORDER BY added_date DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"search": f"%{search_name}%", "value": filter_value, "limit": page_size, "offset": offset_val}

    elif filter_type == "date":
        now = datetime.now()
        if filter_value == "today":
            date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif filter_value == "week":
            date_from = now - timedelta(days=7)
        elif filter_value == "month":
            date_from = now - timedelta(days=30)
        else:
            date_from = None

        stmt = text("""
            SELECT * FROM clients
            WHERE full_name LIKE :search AND added_date >= :date_from
            ORDER BY added_date DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"search": f"%{search_name}%", "date_from": date_from, "limit": page_size, "offset": offset_val}

    else:
        stmt = text("""
            SELECT * FROM clients
            WHERE full_name LIKE :search
            ORDER BY added_date DESC
            LIMIT :limit OFFSET :offset
        """)
        params = {"search": f"%{search_name}%", "limit": page_size, "offset": offset_val}

    result = await session.execute(stmt, params)
    return result.fetchall()


async def show_clients_page(target_message: types.Message, page: int = 1, search_name: str = "", filter_by: str = ""):
    """Обновляет список клиентов с клавиатурой"""
    async with async_session() as session:
        rows = await _call_get_clients(session, search_name, filter_by, page, PAGE_SIZE)

    total_returned = len(rows)
    has_next = total_returned == PAGE_SIZE

    if total_returned == 0:
        text_out = "👥 Клиенты не найдены по заданным критериям."
    else:
        text_out = f"<b>Список клиентов — страница {page}</b>\n\n"
        for r in rows:
            text_out += format_client_card_row(r)

    top_kb = top_clients_kb()
    nav_kb = clients_nav_kb(page, has_next, search_name, filter_by)
    for row in nav_kb.inline_keyboard:
        top_kb.row(*row)

    try:
        await target_message.edit_text(text_out, parse_mode="HTML", reply_markup=top_kb)
    except:
        await target_message.answer(text_out, parse_mode="HTML", reply_markup=top_kb)


@dp.callback_query_handler(lambda c: c.data.startswith("clients_page|"))
async def clients_pagination_callback(callback: types.CallbackQuery):
    await callback.answer()
    try:
        _, page, search_name, filter_by = callback.data.split("|", 3)
        await show_clients_page(callback.message, page=int(page), search_name=search_name, filter_by=filter_by)
    except Exception as e:
        await callback.message.answer(f"Ошибка пагинации: {e}")
