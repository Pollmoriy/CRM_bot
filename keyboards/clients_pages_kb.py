from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def clients_pages_kb(current_page: int, total_pages: int):
    """
    Клавиатура для навигации по страницам клиентов.
    """
    kb = InlineKeyboardMarkup(row_width=3)

    buttons = []

    # Кнопка "Предыдущая"
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"clients_page:{current_page-1}"))
    else:
        buttons.append(InlineKeyboardButton("⬅️", callback_data="ignore"))

    # Показ текущей страницы
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="ignore"))

    # Кнопка "Следующая"
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"clients_page:{current_page+1}"))
    else:
        buttons.append(InlineKeyboardButton("➡️", callback_data="ignore"))

    kb.add(*buttons)
    return kb
