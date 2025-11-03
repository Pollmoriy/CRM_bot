# handlers/clients/view_clients.py
from aiogram import types, Dispatcher
from sqlalchemy import text
from database.db import async_session
from loader import dp
from keyboards.clients_pages_kb import top_clients_kb, clients_nav_kb, filter_values_kb
from datetime import datetime, timedelta

PAGE_SIZE = 5  # сколько клиентов на странице

def format_client_card_row(row) -> str:
    """Красивое форматирование карточки клиента"""
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
    """Получаем клиентов из базы с учётом фильтра и пагинации"""
    filter_type = ""
    filter_value = ""
    if filter_by and "|" in filter_by:
        filter_type, filter_value = filter_by.split("|", maxsplit=1)

    offset_val = (page - 1) * page_size

    # Формируем SQL запрос
    if filter_type == "segment":
        stmt = text(
            "SELECT * FROM clients "
            "WHERE full_name LIKE :search AND segment = :value "
            "ORDER BY added_date DESC "
            "LIMIT :limit OFFSET :offset"
        )
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

        stmt = text(
            "SELECT * FROM clients "
            "WHERE full_name LIKE :search AND added_date >= :date_from "
            "ORDER BY added_date DESC "
            "LIMIT :limit OFFSET :offset"
        )
        params = {"search": f"%{search_name}%", "date_from": date_from, "limit": page_size, "offset": offset_val}

    else:
        stmt = text(
            "SELECT * FROM clients "
            "WHERE full_name LIKE :search "
            "ORDER BY added_date DESC "
            "LIMIT :limit OFFSET :offset"
        )
        params = {"search": f"%{search_name}%", "limit": page_size, "offset": offset_val}

    result = await session.execute(stmt, params)
    rows = result.fetchall()
    return rows


async def show_clients_page(target_message: types.Message, page: int = 1, search_name: str = "", filter_by: str = ""):
    """Показывает страницу клиентов с верхними кнопками, фильтром и пагинацией"""
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

    # Верхние кнопки + фильтр
    top_kb = top_clients_kb()
    # Навигация
    nav_kb = clients_nav_kb(page, has_next, search_name=search_name, filter_by=filter_by)

    # объединяем клавиатуры
    combined_kb = top_kb
    for row in nav_kb.inline_keyboard:
        combined_kb.row(*row)

    try:
        await target_message.edit_text(text_out, parse_mode="HTML", reply_markup=combined_kb)
    except:
        await target_message.answer(text_out, parse_mode="HTML", reply_markup=combined_kb)


# Пагинация
@dp.callback_query_handler(lambda c: c.data.startswith("clients_page|"))
async def clients_pagination_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    try:
        _, page, search_name, filter_by = callback.data.split("|", maxsplit=3)
    except ValueError:
        # fallback если вдруг callback некорректный
        return
    await show_clients_page(callback.message, page=int(page), search_name=search_name, filter_by=filter_by)


# Фильтр: выбор значения
@dp.callback_query_handler(lambda c: c.data.startswith("filter_apply|"))
async def apply_filter_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    try:
        _, filter_type, filter_value = callback.data.split("|", maxsplit=2)
    except ValueError:
        filter_type, filter_value = "", ""
    if filter_type == "none":
        filter_by = ""
    else:
        filter_by = f"{filter_type}|{filter_value}"
    await show_clients_page(callback.message, page=1, search_name="", filter_by=filter_by)


# Фильтр: открытие выбора
@dp.callback_query_handler(lambda c: c.data == "client_filter")
async def select_filter_callback(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    kb = filter_values_kb("segment")  # сначала показываем сегменты
    await callback.message.edit_reply_markup(reply_markup=kb)
