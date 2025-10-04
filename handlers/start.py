from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from database.models import User, db
from states.client_states import REGISTER_NAME, REGISTER_PHONE, REGISTER_EMAIL
from utils.validators import is_valid_email, is_valid_phone
from keyboards.admin_menu import admin_menu_keyboard
from keyboards.manager_menu import manager_menu_keyboard
from keyboards.user_menu import user_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    db.connect()
    user = User.get_or_none(User.tg_id == tg_id)
    db.close()
    if user:
        full_name = user.full_name or "пользователь"
        await update.message.reply_text(f"Привет, {full_name}!")
        if user.role == "admin":
            await update.message.reply_text(
                "Вы вошли как администратор:",
                reply_markup=admin_menu_keyboard()
            )
        elif user.role == "manager":
            await update.message.reply_text(
                "Вы вошли как менеджер:",
                reply_markup=manager_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "Вы вошли как клиент:",
                reply_markup=user_menu_keyboard()
            )
        return

    await update.message.reply_text(
        "Привет! Давай зарегистрируем тебя.\nКак тебя зовут?"
    )
    return REGISTER_NAME

# Получение ФИО
async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("Введите ваш телефон:")
    return REGISTER_PHONE

# Получение телефона
async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not is_valid_phone(phone):
        await update.message.reply_text("Неверный формат телефона. Введите снова (только цифры, можно +):")
        return REGISTER_PHONE
    context.user_data['phone'] = phone
    await update.message.reply_text("Введите ваш email:")
    return REGISTER_EMAIL

# Получение email и сохранение пользователя
async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if not is_valid_email(email):
        await update.message.reply_text("Неверный формат email. Введите снова (пример: user@mail.com):")
        return REGISTER_EMAIL

    context.user_data['email'] = email
    full_name = context.user_data['full_name']
    phone = context.user_data['phone']
    tg_id = update.effective_user.id

    db.connect()
    User.create(tg_id=tg_id, full_name=full_name, phone=phone, email=email)
    db.close()

    await update.message.reply_text(f"Регистрация завершена!")
    return ConversationHandler.END

