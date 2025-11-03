from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def client_menu_kb(for_role: str):
    """
    Меню клиентов:
    - Просмотр списка с кнопками для каждого клиента
    - Добавление нового клиента
    """
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📋 Список клиентов", callback_data="view_clients"),
        InlineKeyboardButton("➕ Добавить клиента", callback_data="client_add")
    )
    return kb
