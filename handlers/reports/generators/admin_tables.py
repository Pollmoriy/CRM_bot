import os
from datetime import datetime, date
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from database.db import async_session_maker
from database.models import Deal, Task, TaskStatus

from matplotlib import pyplot as plt
import pandas as pd

TABLES_DIR = "reports/tables"
os.makedirs(TABLES_DIR, exist_ok=True)


async def generate_admin_sales_table(start_date: date, end_date: date, label: str) -> str:
    """
    Генерирует таблицу продаж по клиентам и сохраняет как PNG.
    Возвращает путь к PNG для вставки в Word.
    """
    print("👥 Генерация таблицы продаж по клиентам")

    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal)
            .options(joinedload(Deal.client), joinedload(Deal.manager))
            .where(Deal.date_created >= datetime.combine(start_date, datetime.min.time()),
                   Deal.date_created <= datetime.combine(end_date, datetime.max.time()))
        )
        deals = result.scalars().all()

    data = []
    for d in deals:
        client_name = d.client.full_name if d.client else "—"

        # Ограничиваем длину названия сделки
        max_len = 20
        deal_name = d.deal_name
        if deal_name and len(deal_name) > max_len:
            deal_name = deal_name[:max_len - 3] + "…"

        stage = d.stage.value if hasattr(d.stage, "value") else d.stage
        manager_name = d.manager.full_name if d.manager else "—"
        created_date = d.date_created.strftime("%d.%m.%Y") if d.date_created else "—"
        data.append([client_name, deal_name, stage, manager_name, created_date])

    if not data:
        data = [["Нет данных", "", "", "", ""]]

    df = pd.DataFrame(data, columns=["Клиент", "Название сделки", "Этап сделки", "Менеджер", "Дата создания"])

    # Сохраняем как PNG
    fig, ax = plt.subplots(figsize=(10, len(df)*0.5 + 1))
    ax.axis("off")
    table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    file_path = os.path.join(TABLES_DIR, f"admin_sales_{label}.png")
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()
    print(f"✅ Таблица продаж сохранена: {file_path}")
    return file_path


async def generate_admin_performance_table(start_date: date, end_date: date, label: str) -> str:
    """
    Генерирует таблицу с показателями сотрудников (создано, выполнено, просрочено, средняя нагрузка)
    и сохраняет как PNG. Возвращает путь к PNG для вставки в Word.
    """
    print("👥 Генерация таблицы сотрудников")

    async with async_session_maker() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.employee))
            .where(Task.deadline >= datetime.combine(start_date, datetime.min.time()),
                   Task.deadline <= datetime.combine(end_date, datetime.max.time()))
        )
        tasks = result.scalars().all()

    employees = {}
    for t in tasks:
        emp_id = t.id_employee or 0
        emp_name = t.employee.full_name if t.employee else "—"
        if emp_id not in employees:
            employees[emp_id] = {"Имя": emp_name, "Создано": 0, "Выполнено": 0, "Просрочено": 0}
        employees[emp_id]["Создано"] += 1
        if t.status == TaskStatus.done:
            employees[emp_id]["Выполнено"] += 1
        if t.status == TaskStatus.overdue:
            employees[emp_id]["Просрочено"] += 1

    data = []
    for emp in employees.values():
        created = emp["Создано"]
        done = emp["Выполнено"]
        overdue = emp["Просрочено"]
        avg_load = round(created, 1)
        data.append([emp["Имя"], created, done, overdue, avg_load])

    if not data:
        data = [["Нет данных", 0, 0, 0, 0]]

    df = pd.DataFrame(data, columns=["Сотрудник", "Создано", "Выполнено", "Просрочено", "Средняя нагрузка"])

    # Сохраняем как PNG
    fig, ax = plt.subplots(figsize=(8, len(df)*0.5 + 1))
    ax.axis("off")
    table = ax.table(cellText=df.values, colLabels=df.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    file_path = os.path.join(TABLES_DIR, f"admin_performance_{label}.png")
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()
    print(f"✅ Таблица сотрудников сохранена: {file_path}")
    return file_path
