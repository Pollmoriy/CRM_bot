# keyboards/clients_pages_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Верхние кнопки
def top_clients_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Поиск", callback_data="client_search"),
        InlineKeyboardButton("🗂 Фильтр", callback_data="client_filter")
    )
    kb.add(
        InlineKeyboardButton("➕ Добавить", callback_data="client_add"),
        InlineKeyboardButton("⬅️ Назад", callback_data="client_back")
    )
    return kb

# Навигация по страницам
def clients_nav_kb(current_page: int, has_next: bool, search_name: str, filter_by: str):
    prev_page = max(current_page - 1, 1)
    next_page = current_page + 1 if has_next else current_page

    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("⬅️", callback_data=f"clients_page|{prev_page}|{search_name}|{filter_by}"),
        InlineKeyboardButton(f"Стр. {current_page}", callback_data="noop"),
        InlineKeyboardButton("➡️", callback_data=f"clients_page|{next_page}|{search_name}|{filter_by}")
    )
    return kb

# Клавиатура выбора фильтра
def filter_options_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("По дате добавления", callback_data="filter|date"),
        InlineKeyboardButton("По сегментации", callback_data="filter|segment"),
        InlineKeyboardButton("Сбросить фильтр", callback_data="filter|none")
    )
    return kb
