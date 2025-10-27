# main.py
from loader import app, init_db
from telegram.ext import CommandHandler

# Тестовая команда
async def start(update, context):
    await update.message.reply_text("Бот запущен. База данных подключена ✅")

def main():
    init_db()
    app.add_handler(CommandHandler("start", start))
    print("🚀 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()

