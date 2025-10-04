from telegram import ReplyKeyboardMarkup

def manager_menu_keyboard():
    buttons = [
        ["👥 Клиенты", "📁 Заказы"],
        ["📝 Задачи", "📊 Отчёты"],
        ["👤 Профиль"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
