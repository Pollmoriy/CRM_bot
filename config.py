import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MySQL
DB_NAME = os.getenv("DB_NAME", "business_manager")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
