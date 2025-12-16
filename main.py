# main.py

import asyncio
from aiogram import executor
from loader import bot, dp, init_db

# Подключаем ВСЕ хэндлеры
import handlers.start
import handlers.clients.menu
import handlers.clients.view_clients
import handlers.deals.menu
import handlers.deals.view_deals
import handlers.deals.history
import handlers.deals.progress
import handlers.deals.tasks
from handlers.admin import users
from handlers.manager import manager_employees
from handlers.reports.reports_menu import register_reports_menu
from handlers.reports.manager_reports import register_manager_reports
from handlers.employee import employee_tasks
from handlers.reports.manager_deals_report import register_manager_deals_report
from handlers.reports.manager_tasks_timeline import register_manager_timeline_report
from handlers.reports.admin_performance_report import register_admin_performance_report
from handlers.reports.admin_deals_report import register_admin_deals_report
from handlers.reports.admin_sales_report import register_admin_sales_report
from handlers.reports.admin_sales_funnel import register_admin_funnel_report
from handlers.reports.admin_timeline import register_admin_timeline_report


# регистрация хендлеров
register_admin_timeline_report(dp)
register_admin_funnel_report(dp)
register_admin_sales_report(dp)
register_admin_deals_report(dp)
register_manager_timeline_report(dp)
register_manager_deals_report(dp)
register_manager_reports(dp)
register_reports_menu(dp)
register_admin_performance_report(dp)


# APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.notifications.reminders import check_task_reminders, check_closed_deals

scheduler = AsyncIOScheduler()


async def on_startup(dp):
    await init_db()
    print("🤖 Бот успешно запущен!")

    # Запускаем периодические задачи (через scheduler)
    # - напоминания о дедлайнах (раз в 24 часа). Для тестирования можно поставить minutes=1
    scheduler.add_job(check_task_reminders, "interval", hours=24, id="task_reminders")
    # - проверка закрытых сделок (раз в 1 час или 24 часа, в зависимости от требований)
    scheduler.add_job(check_closed_deals, "interval", hours=1, id="closed_deals_check")
    scheduler.start()
    print("🕒 Планировщик запущен (jobs: task_reminders, closed_deals_check)")


async def on_shutdown(dp):
    print("🛑 Завершение работы... Закрытие соединений с БД.")
    try:
        await bot.session.close()
    except Exception:
        pass
    scheduler.shutdown(wait=False)


if __name__ == "__main__":
    print("🚀 Запуск бота...")
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
