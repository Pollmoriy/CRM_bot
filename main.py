import asyncio
from loader import bot, dp, init_db
from aiogram import executor
import handlers.start
import handlers.clients.menu
import handlers.clients.view_clients
import handlers.deals.menu


async def on_startup(dp):  # <- обязательно принимать аргумент dp
    await init_db()
    print("Бот запущен и база данных готова!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

