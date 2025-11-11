# keyboards/clients_pages_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def top_clients_kb():
    """
    Верхняя клавиатура для страницы клиентов.
    Сюда можно добавить кнопки 'Поиск', 'Фильтр' и 'Главное меню'.
    """
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Поиск клиента", callback_data="client_search"),
        InlineKeyboardButton("📊 Фильтр", callback_data="client_filter"),
    )
    kb.add(
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_back")
    )
    return kb

def clients_nav_kb(current_page: int, has_next: bool, search_name: str = "", filter_by: str = ""):
    """
    Клавиатура для навигации между страницами клиентов.
    """
    kb = InlineKeyboardMarkup(row_width=2)

    # Кнопки назад/вперед
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"clients_page|{current_page-1}|{search_name}|{filter_by}"
            )
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton(
                "➡️ Далее",
                callback_data=f"clients_page|{current_page+1}|{search_name}|{filter_by}"
            )
        )
    if nav_buttons:
        kb.row(*nav_buttons)

    return kb

def filter_values_kb(filter_type: str):
    """
    Клавиатура значений фильтрации (сегмент или дата).
    """
    kb = InlineKeyboardMarkup(row_width=2)
    if filter_type == "segment":
        kb.add(
            InlineKeyboardButton("VIP", callback_data="filter_apply|segment|vip"),
            InlineKeyboardButton("Regular", callback_data="filter_apply|segment|regular"),
            InlineKeyboardButton("New", callback_data="filter_apply|segment|new"),
        )
    elif filter_type == "date":
        kb.add(
            InlineKeyboardButton("Сегодня", callback_data="filter_apply|date|today"),
            InlineKeyboardButton("Последняя неделя", callback_data="filter_apply|date|week"),
            InlineKeyboardButton("Последний месяц", callback_data="filter_apply|date|month"),
        )
    kb.add(
        InlineKeyboardButton("❌ Сбросить фильтр", callback_data="filter_apply|none|none")
    )
    return kb
