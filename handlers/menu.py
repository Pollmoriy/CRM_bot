from telegram import Update
from telegram.ext import ContextTypes
from database.models import User
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.manager_menu import manager_menu_keyboard
from keyboards.user_menu import user_menu_keyboard
from database.db import db

# Показываем меню пользователю
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    # Получаем пользователя и его роль
    db.connect(reuse_if_open=True)
    user = User.get_or_none(User.tg_id == tg_id)
    db.close()

    if not user:
        await update.message.reply_text("Сначала нужно зарегистрироваться через /start")
        return

    if user.role == "admin":
        keyboard = admin_menu_keyboard()
    elif user.role == "manager":
        keyboard = manager_menu_keyboard()
    else:
        keyboard = user_menu_keyboard()

    await update.message.reply_text("Выберите раздел:", reply_markup=keyboard)

# Обработка нажатий на кнопки
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tg_id = update.effective_user.id

    db.connect(reuse_if_open=True)
    user = User.get_or_none(User.tg_id == tg_id)
    db.close()

    if not user:
        await update.message.reply_text("Сначала нужно зарегистрироваться через /start")
        return

    role = user.role

    # Раздел "Клиенты"
    if text in ["👥 Клиенты", "👥 Мои клиенты"]:
        if role == "user":
            await update.message.reply_text("Ваши клиенты")
        else:
            await update.message.reply_text("Все клиенты")

    # Раздел "Заказы"
    elif text in ["📁 Заказы", "📁 Мои заказы"]:
        if role == "user":
            await update.message.reply_text("Ваши заказы")
        else:
            await update.message.reply_text("Все заказы")

    # Раздел "Задачи"
    elif text in ["📝 Задачи", "📝 Мои задачи"]:
        if role == "user":
            await update.message.reply_text("Ваши задачи")
        else:
            await update.message.reply_text("Все задачи")

    # Раздел "Отчёты"
    elif text in ["📊 Отчёты", "📊 Моя статистика"]:
        if role == "user":
            await update.message.reply_text("Ваша статистика")
        else:
            await update.message.reply_text("Статистика команды / компании")

    # Раздел "Настройки" (только админ)
    elif text == "⚙️ Настройки":
        if role == "admin":
            await update.message.reply_text("Раздел настроек")
        else:
            await update.message.reply_text("У вас нет доступа к настройкам")

    # Раздел "Профиль"
    elif text == "👤 Профиль":
        await update.message.reply_text(f"Профиль пользователя: {user.full_name}\nEmail: {user.email}\nТелефон: {user.phone}\nРоль: {user.role}")

    else:
        await update.message.reply_text("Нажмите кнопку из меню")
