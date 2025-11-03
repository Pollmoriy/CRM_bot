# keyboards/client_menu_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def client_menu_kb(for_role: str):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📋 Просмотр списка", callback_data="client_view")
    )
    kb.add(
        InlineKeyboardButton("➕ Добавить клиента", callback_data="client_add"),
        InlineKeyboardButton("✏️ Изменить клиента", callback_data="client_edit")
    )
    # удаление — admin/manager
    if for_role in ("admin", "manager"):
        kb.add(InlineKeyboardButton("❌ Удалить клиента", callback_data="client_delete"))
    return kb
