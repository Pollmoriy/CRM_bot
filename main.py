# main.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN

# обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой CRM-бот 😊")

def main():
    # создаём приложение
    app = Application.builder().token(BOT_TOKEN).build()

    # добавляем обработчик команды
    app.add_handler(CommandHandler("start", start))

    print("Бот запущен...")
    # запускаем polling
    app.run_polling()

if __name__ == "__main__":
    main()
