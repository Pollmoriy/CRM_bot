# main.py
from database.db import db
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers.start import start, register_name, register_phone, register_email
from states.client_states import REGISTER_NAME, REGISTER_PHONE, REGISTER_EMAIL
from config import BOT_TOKEN

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REGISTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone)],
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

