from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

employee_menu = ReplyKeyboardMarkup(resize_keyboard=True)
employee_menu.add(
    KeyboardButton("👥 Мои клиенты"),
    KeyboardButton("💼 Мои сделки"),
)
employee_menu.add(
    KeyboardButton("✅ Мои задачи"),
    KeyboardButton("📊 Отчёты")
)
