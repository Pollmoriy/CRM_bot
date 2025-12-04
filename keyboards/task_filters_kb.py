# keyboards/task_filters_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_filters_kb():
    """
    Возвращает клавиатуру фильтров для задач:
    - по статусу: все, новые, в работе, выполненные, просроченные
    - по приоритету: все, низкий, средний, высокий
    """
    kb = InlineKeyboardMarkup(row_width=2)

    # Фильтры по статусу
    kb.add(
        InlineKeyboardButton("Все статусы", callback_data="filter_status_all"),
        InlineKeyboardButton("Новые", callback_data="filter_status_new"),
        InlineKeyboardButton("В работе", callback_data="filter_status_in_progress"),
        InlineKeyboardButton("Выполненные", callback_data="filter_status_done"),
        InlineKeyboardButton("Просроченные", callback_data="filter_status_overdue")
    )

    # Фильтры по приоритету
    kb.add(
        InlineKeyboardButton("Все приоритеты", callback_data="filter_priority_all"),
        InlineKeyboardButton("Низкий", callback_data="filter_priority_low"),
        InlineKeyboardButton("Средний", callback_data="filter_priority_medium"),
        InlineKeyboardButton("Высокий", callback_data="filter_priority_high")
    )

    return kb
