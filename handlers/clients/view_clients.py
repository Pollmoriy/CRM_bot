from aiogram import types
from sqlalchemy import text
from database.db import async_session
from loader import dp
from keyboards.clients_pages_kb import top_clients_kb, clients_nav_kb

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
    stmt = text("CALL get_clients(:search_name, :filter_by, :page, :page_size)")
    result = await session.execute(stmt, {
        "search_name": search_name or "",
        "filter_by": filter_by or "",
        "page": page,
        "page_size": page_size
    })
    rows = result.fetchall()
    return rows

async def show_clients_page(target_message: types.Message, page: int = 1, search_name: str = "", filter_by: str = ""):
    try:
        await target_message.edit_text("Загружаю список клиентов...")
    except:
        await target_message.answer("Загружаю список клиентов...")

    async with async_session() as session:
        try:
            rows = await _call_get_clients(session, search_name, filter_by, page, PAGE_SIZE)
        except Exception as e:
            await target_message.answer(f"Ошибка при загрузке клиентов: {e}")
            return

    total_returned = len(rows)
    has_next = total_returned == PAGE_SIZE

    if total_returned == 0:
        text_out = "👥 Клиенты не найдены по заданным критериям."
    else:
        text_out = f"<b>Список клиентов — страница {page}</b>\n\n"
        for r in rows:
            text_out += format_client_card_row(r)

    # Верхние кнопки и навигация
    top_kb = top_clients_kb()
    nav_kb = clients_nav_kb(page, has_next, search_name=search_name, filter_by=filter_by)

    # Объединяем клавиатуры (верхние кнопки + навигация)
    combined_kb = top_kb
    for row in nav_kb.inline_keyboard:
        combined_kb.row(*row)

    try:
        await target_message.edit_text(text_out, parse_mode="HTML", reply_markup=combined_kb)
    except Exception:
        await target_message.answer(text_out, parse_mode="HTML", reply_markup=combined_kb)

# CALLBACK для переключения страниц
@dp.callback_query_handler(lambda c: c.data.startswith("clients_page|"))
async def clients_pagination_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    _, page, search_name, filter_by = callback.data.split("|")
    page = int(page)
    await show_clients_page(callback.message, page=page, search_name=search_name, filter_by=filter_by)
