from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def reports_menu_kb(role: str):
    # row_width=2 → по две кнопки в строке
    kb = InlineKeyboardMarkup(row_width=2)

    if role == "manager":
        kb.add(
            InlineKeyboardButton("📊 Отчёт по задачам сотрудников", callback_data="report_manager_tasks"),
            InlineKeyboardButton("📈 Прогресс сделок", callback_data="report_manager_deals"),
            InlineKeyboardButton("📅 Динамика задач", callback_data="report_manager_timeline"),
        )

    elif role == "admin":
        kb.add(
            InlineKeyboardButton("📊 Активность сотрудников", callback_data="report_admin_performance"),
            InlineKeyboardButton("📈 Прогресс сделок", callback_data="report_admin_deals"),
            InlineKeyboardButton("💰 Продажи по клиентам", callback_data="report_admin_sales"),
            InlineKeyboardButton("🪣 Воронка продаж", callback_data="report_admin_funnel"),
            InlineKeyboardButton("📅 Динамика по периодам", callback_data="report_admin_timeline"),
            InlineKeyboardButton("🤖 Сделать отчет", callback_data="report"),
        )

    return kb
