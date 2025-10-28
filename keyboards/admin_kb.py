from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(
    KeyboardButton("⚙️ Пользователи"),
    KeyboardButton("📈 Статистика"),
)
admin_menu.add(
    KeyboardButton("👥 Клиенты"),
    KeyboardButton("💼 Сделки"),
)
admin_menu.add(
    KeyboardButton("📢 Рассылки"),
    KeyboardButton("📊 Отчёты")
)
