# loader.py
from telegram.ext import Application
from config import BOT_TOKEN
from database.models import db, User

# --- Подключение к БД и создание таблиц (если не созданы) ---
def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([User])
    print("✅ Таблицы инициализированы")

# --- Инициализация бота ---
app = Application.builder().token(BOT_TOKEN).build()
