# handlers/reports/manager_reports.py
import os
from aiogram import types, Dispatcher
from sqlalchemy import select
from database.db import async_session_maker
from database.models import User, Task, TaskStatus
import matplotlib.pyplot as plt
from datetime import date

async def report_manager_tasks_cb_handler(query: types.CallbackQuery):
    """Хендлер для кнопки 'Отчёт по задачам сотрудников' (менеджер)"""
    print(f"📌 Callback report_manager_tasks_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт...")

    async with async_session_maker() as session:
        # ORM-запрос через select(User)
        result = await session.execute(select(User).where(User.telegram_id == str(query.from_user.id)))
        user_obj = result.scalar_one_or_none()

        if not user_obj:
            await query.message.answer("❌ Пользователь не найден в базе.")
            print(f"❌ Пользователь {query.from_user.id} не найден")
            return

        print(f"✅ Найден пользователь: {user_obj.full_name}, роль: {user_obj.role.value}")

        # --- Получаем задачи менеджера и подчиненных ---
        result_tasks = await session.execute(select(Task))
        tasks = result_tasks.scalars().all()
        print(f"ℹ️ Всего задач в БД: {len(tasks)}")

        data = {}
        for task in tasks:
            if task.id_employee is None:
                continue

            # Получаем пользователя-исполнителя задачи
            result_emp = await session.execute(select(User).where(User.id_user == task.id_employee))
            emp_obj = result_emp.scalar_one_or_none()
            if not emp_obj:
                continue

            # Учитываем только свои задачи и задачи подчиненных
            if emp_obj.id_user != user_obj.id_user and emp_obj.manager_id != user_obj.id_user:
                continue

            if emp_obj.full_name not in data:
                data[emp_obj.full_name] = {
                    TaskStatus.new: 0,
                    TaskStatus.in_progress: 0,
                    TaskStatus.done: 0,
                    TaskStatus.overdue: 0
                }
            data[emp_obj.full_name][TaskStatus(task.status)] += 1

        if not data:
            await query.message.answer("ℹ️ Нет данных для отчёта.")
            print("ℹ️ Нет данных для отчёта")
            return

        print(f"ℹ️ Данные для отчёта: {data}")

        # --- Строим эстетичную горизонтальную стековую диаграмму ---
        fig, ax = plt.subplots(figsize=(10, 6))

        employees = list(data.keys())
        statuses = [TaskStatus.done, TaskStatus.in_progress, TaskStatus.new, TaskStatus.overdue]
        colors = {
            TaskStatus.done: "#4CAF50",  # зелёный
            TaskStatus.in_progress: "#2196F3",  # синий
            TaskStatus.new: "#FFC107",  # жёлтый
            TaskStatus.overdue: "#F44336",  # красный
        }

        # Инициализация нижней границы для стека
        bottoms = [0] * len(employees)

        for status in statuses:
            counts = [data[e][status] for e in employees]
            ax.barh(employees, counts, left=bottoms, color=colors[status], label=status.name.replace("_", " ").title())
            # Добавляем числа внутри полос
            for i, count in enumerate(counts):
                if count > 0:
                    ax.text(bottoms[i] + count / 2, i, str(count),
                            va='center', ha='center', color='white', fontsize=10, fontweight='bold')
            # Обновляем нижнюю границу стека
            bottoms = [bottoms[i] + counts[i] for i in range(len(employees))]

        ax.set_xlabel("Количество задач", fontsize=12)
        ax.set_title(f"Отчёт по задачам сотрудников ({date.today()})", fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Опционально: ставим топ-менеджеров сверху
        ax.legend(title="Статус задач", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Создаём папку, если её нет
        os.makedirs("reports/images", exist_ok=True)

        # Сохраняем файл
        filename = "reports/images/manager_tasks_report.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        print(f"✅ Диаграмма сохранена: {filename}")

        await query.message.answer_photo(
            types.InputFile(filename),
            caption="📊 Отчёт по задачам сотрудников"
        )
        print(f"🎯 Отчёт отправлен пользователю: {user_obj.full_name}")


def register_manager_reports(dp: Dispatcher):
    """Регистрация хендлера коллбэка для отчёта менеджера"""
    dp.register_callback_query_handler(
        report_manager_tasks_cb_handler,
        lambda c: c.data == "report_manager_tasks"
    )
    print("✅ Хендлер report_manager_tasks_cb_handler зарегистрирован")
