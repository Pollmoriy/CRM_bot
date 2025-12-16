# handlers/reports/admin_tasks_timeline.py
import os
from datetime import date, timedelta

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.db import async_session_maker
from database.models import User, Task, TaskStatus


async def report_admin_timeline_cb_handler(query: types.CallbackQuery):
    """📅 Динамика задач по всем сотрудникам (админ)"""
    print(f"📌 Callback report_admin_timeline_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую динамику задач для всех сотрудников...")

    async with async_session_maker() as session:
        # --- Загружаем всех пользователей вместе с их задачами асинхронно ---
        result = await session.execute(
            select(User).options(selectinload(User.tasks))
        )
        users = result.scalars().all()

        if not users:
            await query.message.answer("ℹ️ Нет данных о сотрудниках.")
            return

        print(f"ℹ️ Найдено сотрудников: {len(users)}")

        # --- Период отчёта ---
        days = 30
        today = date.today()
        start_date = today - timedelta(days=days)
        dates = [start_date + timedelta(days=i) for i in range(days + 1)]

        # --- Инициализация данных по дням ---
        created = {d: 0 for d in dates}
        done = {d: 0 for d in dates}
        overdue = {d: 0 for d in dates}

        # --- Обработка задач всех сотрудников ---
        for user in users:
            for task in user.tasks:
                if not task.id_employee:
                    continue

                # --- Создание ---
                if task.deadline and start_date <= task.deadline <= today:
                    created[task.deadline] += 1

                # --- Завершение ---
                if task.status == TaskStatus.done and task.date_completed:
                    if start_date <= task.date_completed <= today:
                        done[task.date_completed] += 1

                # --- Просрочка ---
                if (
                    task.deadline
                    and task.deadline < today
                    and task.status != TaskStatus.done
                    and start_date <= task.deadline <= today
                ):
                    overdue[task.deadline] += 1

        if not any(created.values()) and not any(done.values()) and not any(overdue.values()):
            await query.message.answer("ℹ️ Нет данных для отчёта за выбранный период.")
            return

        # --- График ---
        fig, ax = plt.subplots(figsize=(12, 6))

        x_labels = [d.strftime("%d.%m") for d in dates]

        ax.plot(
            x_labels,
            list(created.values()),
            label="Создано 🟦",
            color="#1565C0",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            list(done.values()),
            label="Завершено 🟩",
            color="#2E7D32",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            list(overdue.values()),
            label="Просрочено 🟥",
            color="#C62828",
            linewidth=2.5,
            marker="o"
        )

        # --- Настройка графика ---
        ax.set_title(
            f"📅 Динамика задач всех сотрудников за последние {days} дней",
            fontsize=16,
            fontweight="bold"
        )
        ax.set_xlabel("Дата", fontsize=12)
        ax.set_ylabel("Количество задач", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=11)
        plt.xticks(rotation=45)

        plt.tight_layout()

        # --- Сохранение диаграммы ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_tasks_timeline.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        # --- Подробная подпись ---
        total_created = sum(created.values())
        total_done = sum(done.values())
        total_overdue = sum(overdue.values())
        total_tasks = total_created + total_done + total_overdue

        caption = (
            f"📊 Динамика задач всех сотрудников за последние {days} дней\n\n"
            f"Синим — создано: {total_created} задач\n"
            f"Зелёным — завершено: {total_done} задач\n"
            f"Красным — просрочено: {total_overdue} задач\n"
            f"Общее количество задач за период: {total_tasks}\n\n"
            f"Процент выполнения: {round((total_done / total_tasks * 100) if total_tasks else 0, 2)}%\n"
            f"Процент просроченных: {round((total_overdue / total_tasks * 100) if total_tasks else 0, 2)}%\n"
            f"Среднее создание задач в день: {round(total_created / days, 2)}\n"
            f"Среднее завершение задач в день: {round(total_done / days, 2)}\n"
            f"Среднее количество просроченных задач в день: {round(total_overdue / days, 2)}\n\n"
            f"🤖 Рекомендации ИИ:\n"
            f"Используйте график для оценки загруженности команды, своевременного распределения задач и предотвращения просрочек. "
            f"При необходимости перераспределяйте задачи между сотрудниками для равномерной загрузки."
        )

        # --- Отправка ---
        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print(f"🎯 Диаграмма динамики задач для админа отправлена.")


def register_admin_timeline_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_timeline_cb_handler,
        lambda c: c.data == "report_admin_timeline"
    )
    print("✅ Хендлер report_admin_timeline_cb_handler зарегистрирован")
