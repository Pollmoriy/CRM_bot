import os
from datetime import date, timedelta
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import select

from database.db import async_session_maker
from database.models import Task, TaskStatus


async def generate_admin_tasks_timeline_diagram(
    start_date: date,
    end_date: date,
    period_label: str
):
    """
    Диаграмма «Динамика задач» по статусам:
    • new — новые
    • in_progress — в работе
    • done — завершённые
    • overdue — просроченные
    """

    async with async_session_maker() as session:
        result = await session.execute(select(Task))
        tasks = result.scalars().all()

    # --- словари для подсчёта ---
    status_counts = {
        TaskStatus.new: defaultdict(int),
        TaskStatus.in_progress: defaultdict(int),
        TaskStatus.done: defaultdict(int),
        TaskStatus.overdue: defaultdict(int),
    }

    # --- заполнение по статусам ---
    for task in tasks:
        task_dates = []
        if task.status == TaskStatus.done and task.date_completed:
            task_dates = [task.date_completed]
        elif task.status in (TaskStatus.new, TaskStatus.in_progress, TaskStatus.overdue) and task.deadline:
            task_dates = [task.deadline]

        for d in task_dates:
            if start_date <= d <= end_date:
                status_counts[task.status][d] += 1

    if all(len(v) == 0 for v in status_counts.values()):
        print("⚠️ Нет задач для диаграммы динамики")
        return None

    days_delta = (end_date - start_date).days

    # --- формирование X-оси ---
    if days_delta <= 60:
        x_dates = [start_date + timedelta(days=i) for i in range(days_delta + 1)]
        locator = mdates.DayLocator(interval=max(1, days_delta // 10))
        date_fmt = "%d.%m"
    else:
        # агрегация по месяцам
        x_dates_set = set()
        for status_dict in status_counts.values():
            for d in status_dict.keys():
                x_dates_set.add(date(d.year, d.month, 1))
        x_dates = sorted(x_dates_set)
        locator = mdates.MonthLocator(interval=1)
        date_fmt = "%m.%Y"

    # --- значения по каждому статусу ---
    y_values = {}
    for status, counts in status_counts.items():
        if days_delta <= 60:
            y_values[status] = [counts.get(d, 0) for d in x_dates]
        else:
            # по месяцам
            monthly_counts = defaultdict(int)
            for d, c in counts.items():
                key = date(d.year, d.month, 1)
                monthly_counts[key] += c
            y_values[status] = [monthly_counts.get(d, 0) for d in x_dates]

    # --- цвета и подписи ---
    colors = {
        TaskStatus.new: "#FFA500",          # оранжевый
        TaskStatus.in_progress: "#1E90FF",  # синий
        TaskStatus.done: "#28A745",         # зелёный
        TaskStatus.overdue: "#DC3545",      # красный
    }

    labels = {
        TaskStatus.new: "Новые",
        TaskStatus.in_progress: "В работе",
        TaskStatus.done: "Завершённые",
        TaskStatus.overdue: "Просроченные",
    }

    # --- построение графика ---
    plt.figure(figsize=(12, 6))
    for status, y_vals in y_values.items():
        plt.plot(
            x_dates,
            y_vals,
            marker="o",
            linewidth=2,
            label=labels[status],
            color=colors[status]
        )

    plt.title(f"Динамика задач ({period_label})", fontsize=15, fontweight="bold")
    plt.xlabel("Период")
    plt.ylabel("Количество задач")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_fmt))
    ax.xaxis.set_major_locator(locator)

    plt.xticks(rotation=45)
    plt.tight_layout()

    # --- сохранение ---
    os.makedirs("reports/images", exist_ok=True)
    filename = f"reports/images/admin_tasks_timeline_{period_label}.png"
    plt.savefig(filename, dpi=150)
    plt.close()

    print(f"✅ Диаграмма динамики задач (по всем статусам) сохранена: {filename}")
    return filename
