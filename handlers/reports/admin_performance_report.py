# handlers/reports/admin_performance_report.py

import os
from datetime import date

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Task, TaskStatus


async def report_admin_performance_cb_handler(query: types.CallbackQuery):
    """📊 Активность сотрудников (для админа)"""
    print(f"📌 Callback report_admin_performance_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по активности сотрудников...")

    async with async_session_maker() as session:
        # --- Получаем всех сотрудников ---
        result_users = await session.execute(select(User))
        users = result_users.scalars().all()

        if not users:
            await query.message.answer("❌ Нет данных по сотрудникам.")
            return

        # --- Получаем все задачи ---
        result_tasks = await session.execute(select(Task))
        tasks = result_tasks.scalars().all()

        # --- Подготовка данных ---
        data = {}
        for task in tasks:
            if not task.id_employee:
                continue

            result_emp = await session.execute(select(User).where(User.id_user == task.id_employee))
            employee = result_emp.scalar_one_or_none()
            if not employee:
                continue

            if employee.full_name not in data:
                data[employee.full_name] = {
                    TaskStatus.new: 0,
                    TaskStatus.in_progress: 0,
                    TaskStatus.done: 0,
                    TaskStatus.overdue: 0
                }

            data[employee.full_name][TaskStatus(task.status)] += 1

        if not data:
            await query.message.answer("ℹ️ Нет данных для отчёта.")
            return

        # --- Строим диаграмму ---
        employees = list(data.keys())
        statuses = [TaskStatus.done, TaskStatus.in_progress, TaskStatus.new, TaskStatus.overdue]

        colors = {
            TaskStatus.done: "#2E7D32",
            TaskStatus.in_progress: "#1565C0",
            TaskStatus.new: "#F9A825",
            TaskStatus.overdue: "#C62828",
        }

        fig, ax = plt.subplots(figsize=(12, 8))
        bottoms = [0] * len(employees)

        for status in statuses:
            counts = [data[e][status] for e in employees]
            ax.barh(
                employees,
                counts,
                left=bottoms,
                color=colors[status],
                label=status.name.replace("_", " ").title()
            )
            bottoms = [bottoms[i] + counts[i] for i in range(len(employees))]

        # --- Подписи над диаграммой ---
        total_tasks = sum(sum(v.values()) for v in data.values())
        caption_lines = ["Сводка по всем сотрудникам:"]
        for status in statuses:
            count = sum(v[status] for v in data.values())
            percent = round((count / total_tasks * 100) if total_tasks else 0, 1)
            caption_lines.append(f"• {status.name.replace('_', ' ').title()}: {count} ({percent}%)")
        caption_lines.append(f"• Всего задач: {total_tasks}")
        caption = "\n".join(caption_lines)

        ax.set_xlabel("Количество задач", fontsize=12)
        ax.set_title(f"📊 Активность сотрудников (на {date.today()})", fontsize=14, fontweight="bold")
        ax.legend()
        plt.tight_layout()

        # --- Сохраняем ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_performance_report.png"
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"✅ Диаграмма сохранена: {filename}")

        # --- Отправка ---
        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print("🎯 Отчёт по активности сотрудников отправлен.")


# 🔌 Регистрация
def register_admin_performance_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_performance_cb_handler,
        lambda c: c.data == "report_admin_performance"
    )
    print("✅ Хендлер report_admin_performance_cb_handler зарегистрирован")
