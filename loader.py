from telegram.ext import Updater
from config import BOT_TOKEN

# Создаём updater и dispatcher
updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher
