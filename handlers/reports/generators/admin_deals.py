# handlers/reports/generators/admin_deals.py
import os
from datetime import date
import matplotlib.pyplot as plt
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import Deal, DealStage

async def generate_admin_deals_diagram(start_date: date, end_date: date, period_label: str) -> str:
    """Прогресс сделок всех сотрудников за период"""

    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal.stage, func.count(Deal.id_deal))
            .where(Deal.date_created >= start_date, Deal.date_created <= end_date)
            .group_by(Deal.stage)
        )
        rows = result.all()

    # --- Подготовка данных ---
    raw = {stage.value if hasattr(stage, "value") else stage: count for stage, count in rows}

    stages = ["Новая", "В работе", "Приостановлена", "Закрыта"]
    counts = [raw.get(stage, 0) for stage in stages]
    total = sum(counts)

    if total == 0:
        print("ℹ️ Сделок нет для выбранного периода")
        return ""

    percentages = [round(c / total * 100, 1) for c in counts]

    colors = {
        "Новая": "#4C72B0",
        "В работе": "#DD8452",
        "Приостановлена": "#8172B2",
        "Закрыта": "#55A868",
    }

    # --- Построение диаграммы ---
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(stages, counts, color=[colors[s] for s in stages], width=0.6)
    for i, bar in enumerate(bars):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.1,
            f"{counts[i]} ({percentages[i]}%)",
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    ax.set_ylabel("Количество сделок")
    ax.set_xlabel("Этап сделки")
    ax.set_title(f"Прогресс сделок всех сотрудников ({period_label})")
    ax.set_ylim(0, max(counts) + 3)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    os.makedirs("reports/images", exist_ok=True)
    filename = f"reports/images/admin_deals_progress_{period_label}.png"
    plt.savefig(filename, dpi=150)
    plt.close()

    print(f"✅ Диаграмма прогресса сделок сохранена: {filename}")
    return filename
