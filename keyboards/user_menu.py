from telegram import ReplyKeyboardMarkup

def user_menu_keyboard():
    buttons = [
        ["👥 Мои клиенты", "📁 Мои заказы"],
        ["📝 Мои задачи", "📊 Моя статистика"],
        ["👤 Профиль"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
