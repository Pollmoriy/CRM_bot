# keyboards/deal_menu_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def deal_menu_kb(role: str):
    kb = InlineKeyboardMarkup(row_width=2)

    if role in ("admin", "manager"):
        kb.add(
            InlineKeyboardButton("📋 Просмотр сделок", callback_data="deal_view"),
            InlineKeyboardButton("➕ Добавить сделку", callback_data="deal_add")
        )
        kb.add(
            InlineKeyboardButton("✏️ Изменить", callback_data="deal_edit"),
            InlineKeyboardButton("🗑️ Удалить", callback_data="deal_delete")
        )
    else:  # сотрудник
        kb.add(InlineKeyboardButton("📋 Мои сделки", callback_data="deal_view"))

    kb.add(InlineKeyboardButton("↩️ Назад", callback_data="back_to_main"))
    return kb
