from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

manager_menu = ReplyKeyboardMarkup(resize_keyboard=True)
manager_menu.add(
    KeyboardButton("👥 Клиенты"),
    KeyboardButton("💼 Сделки"),
)
manager_menu.add(
    KeyboardButton("🧑‍💼 Сотрудники"),
    KeyboardButton("📢 Рассылки")
)
manager_menu.add(
    KeyboardButton("📊 Отчёты")
)
