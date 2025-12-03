from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def deal_menu_kb(role: str):
    kb = InlineKeyboardMarkup(row_width=1)
    if role in ["admin", "manager"]:
        kb.add(
            InlineKeyboardButton("📋 Список сделок", callback_data="deal_view"),
            InlineKeyboardButton("➕ Добавить сделку", callback_data="deal_add"),
            InlineKeyboardButton("✏️ Редактировать сделку", callback_data="deal_edit"),
            InlineKeyboardButton("🗑 Удалить сделку", callback_data="deal_delete"),
        )
    else:  # employee
        kb.add(
            InlineKeyboardButton("Мои сделки", callback_data="deal_view")
        )
    return kb
