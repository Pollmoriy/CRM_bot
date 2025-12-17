# handlers/reports/generators/admin_funnel.py
import os
from collections import OrderedDict
import matplotlib.pyplot as plt
from sqlalchemy import select, func
from datetime import date

from database.db import async_session_maker
from database.models import Deal

async def generate_admin_sales_funnel(start_date: date, end_date: date, period_label: str) -> str:
    """Воронка продаж за период"""

    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal.stage, func.count(Deal.id_deal))
            .where(Deal.date_created >= start_date, Deal.date_created <= end_date)
            .group_by(Deal.stage)
        )
        rows = result.all()

    raw = {stage.value if hasattr(stage, "value") else stage: count for stage, count in rows}

    stages = OrderedDict([
        ("Новая", raw.get("Новая", 0)),
        ("В работе", raw.get("В работе", 0)),
        ("Приостановлена", raw.get("Приостановлена", 0)),
        ("Закрыта", raw.get("Закрыта", 0)),
    ])

    values = list(stages.values())
    total_deals = sum(values)
    if total_deals == 0:
        print("ℹ️ Недостаточно данных для построения воронки")
        return ""

    # --- Построение воронки ---
    fig, ax = plt.subplots(figsize=(8, 6))
    widths = [1.0, 0.78, 0.56, 0.38]
    colors = ["#D0E1F9", "#4C72B0", "#4C72B0", "#4C72B0"]

    for i, (label, value, width) in enumerate(zip(stages.keys(), values, widths)):
        left = 0.5 - width / 2
        ax.barh(y=i, width=width, left=left, height=1.0, color=colors[i], linewidth=0)
        ax.text(0.5, i, f"{label}\n{value} сделок", ha="center", va="center", fontsize=12, fontweight="bold", color="#FFFFFF")

    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.set_title(f"Воронка продаж ({period_label})", fontsize=15, fontweight="bold", pad=20)

    for spine in ax.spines.values():
        spine.set_visible(False)

    os.makedirs("reports/images", exist_ok=True)
    filename = f"reports/images/admin_sales_funnel_{period_label}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"✅ Воронка продаж сохранена: {filename}")
    return filename
