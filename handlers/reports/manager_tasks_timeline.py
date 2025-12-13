# handlers/reports/manager_tasks_timeline.py
import os
from datetime import date, timedelta

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Task, TaskStatus


async def report_manager_timeline_cb_handler(query: types.CallbackQuery):
    """📅 Динамика задач (менеджер)"""
    print(f"📌 Callback report_manager_timeline_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую динамику задач...")

    async with async_session_maker() as session:
        # --- Получаем менеджера ---
        result = await session.execute(
            select(User).where(User.telegram_id == str(query.from_user.id))
        )
        manager = result.scalar_one_or_none()

        if not manager:
            await query.message.answer("❌ Пользователь не найден.")
            return

        print(f"✅ Менеджер: {manager.full_name}")

        # --- Период отчёта ---
        days = 30
        today = date.today()
        start_date = today - timedelta(days=days)

        # --- Получаем все задачи ---
        result_tasks = await session.execute(select(Task))
        tasks = result_tasks.scalars().all()
        print(f"ℹ️ Всего задач в БД: {len(tasks)}")

        # --- Инициализация данных по дням ---
        dates = [start_date + timedelta(days=i) for i in range(days + 1)]
        created = {d: 0 for d in dates}
        done = {d: 0 for d in dates}
        overdue = {d: 0 for d in dates}

        for task in tasks:
            if not task.id_employee:
                continue

            # --- Получаем исполнителя ---
            result_emp = await session.execute(
                select(User).where(User.id_user == task.id_employee)
            )
            employee = result_emp.scalar_one_or_none()
            if not employee:
                continue

            # --- Только свои и подчинённые ---
            if employee.id_user != manager.id_user and employee.manager_id != manager.id_user:
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
        fig, ax = plt.subplots(figsize=(11, 6))

        x_labels = [d.strftime("%d.%m") for d in dates]

        ax.plot(
            x_labels,
            created.values(),
            label="Создано",
            color="#1565C0",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            done.values(),
            label="Завершено",
            color="#2E7D32",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            overdue.values(),
            label="Просрочено",
            color="#C62828",
            linewidth=2.5,
            marker="o"
        )

        ax.set_title(
            f"📅 Динамика задач за последние {days} дней",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel("Дата", fontsize=11)
        ax.set_ylabel("Количество задач", fontsize=11)

        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # --- Сохранение ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/manager_tasks_timeline.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        print(f"✅ Диаграмма сохранена: {filename}")

        await query.message.answer_photo(
            types.InputFile(filename),
            caption="📅 Динамика задач (последние 30 дней)"
        )


def register_manager_timeline_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_manager_timeline_cb_handler,
        lambda c: c.data == "report_manager_timeline"
    )
    print("✅ Хендлер report_manager_timeline_cb_handler зарегистрирован")
