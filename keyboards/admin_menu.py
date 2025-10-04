from telegram import ReplyKeyboardMarkup

def admin_menu_keyboard():
    buttons = [
        ["👥 Клиенты", "📁 Заказы"],
        ["📝 Задачи", "📊 Отчёты"],
        ["⚙️ Настройки", "👤 Профиль"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
