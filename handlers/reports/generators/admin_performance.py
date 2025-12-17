# handlers/reports/generators/admin_performance.py
import os
from datetime import date
import matplotlib.pyplot as plt
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import User, Task

async def generate_admin_performance_diagram(start_date: date, end_date: date, period_label: str) -> str:
    """Диаграмма активности сотрудников: количество выполненных задач за период"""

    async with async_session_maker() as session:
        # Получаем всех сотрудников
        result_users = await session.execute(select(User))
        users = result_users.scalars().all()

        user_names = []
        completed_tasks = []

        for user in users:
            result_tasks = await session.execute(
                select(func.count(Task.id_task))
                .where(
                    Task.id_employee == user.id_user,
                    Task.date_completed != None,
                    Task.date_completed >= start_date,
                    Task.date_completed <= end_date
                )
            )
            count = result_tasks.scalar() or 0
            user_names.append(user.full_name)
            completed_tasks.append(count)

    # --- Построение диаграммы ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(user_names, completed_tasks, color="#4C72B0")
    ax.set_xlabel("Выполнено задач")
    ax.set_title(f"Общая активность сотрудников ({period_label})")
    plt.tight_layout()

    # --- Сохранение ---
    os.makedirs("reports/images", exist_ok=True)
    filename = f"reports/images/admin_performance_report_{period_label}.png"
    plt.savefig(filename, dpi=150)
    plt.close()

    print(f"✅ Диаграмма производительности сохранена: {filename}")
    return filename
