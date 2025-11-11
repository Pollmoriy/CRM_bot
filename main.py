# main.py
import asyncio
from aiogram import executor
from loader import bot, dp, init_db
import handlers.start
import handlers.clients.menu
import handlers.clients.view_clients
import handlers.deals.menu


async def on_startup(dp):
    await init_db()
    print("🤖 Бот успешно запущен!")


async def on_shutdown(dp):
    print("🛑 Завершение работы... Закрытие соединений с БД.")
    await bot.session.close()


if __name__ == "__main__":
    try:
        print("🚀 Запуск бота...")
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    except (KeyboardInterrupt, SystemExit):
        print("❌ Бот остановлен вручную.")
