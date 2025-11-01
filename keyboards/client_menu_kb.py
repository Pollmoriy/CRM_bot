from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def client_menu_kb(for_role: str):
    """
    Возвращает InlineKeyboardMarkup для меню Клиентов.
    for_role: 'admin' | 'manager' | 'employee'
    (менеджер и админ видят все кнопки, сотрудник — без удаления)
    """
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("➕ Добавить клиента", callback_data="client_add"),
        InlineKeyboardButton("✏️ Изменить клиента", callback_data="client_edit")
    )
    # просмотр списка — всем
    kb.add(InlineKeyboardButton("📋 Просмотр списка", callback_data="client_view"))

    # удаление — только admin/manager
    if for_role in ("admin", "manager"):
        kb.add(InlineKeyboardButton("❌ Удалить клиента", callback_data="client_delete"))

    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="client_back"))
    return kb
