# handlers/reports/generators/admin_sales.py
import os
from datetime import date
import matplotlib.pyplot as plt
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import Deal

async def generate_admin_sales_diagram(start_date: date, end_date: date, period_label: str) -> str:
    """Диаграмма продаж по клиентам за период"""

    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal.id_client, func.count(Deal.id_deal))
            .where(Deal.date_created >= start_date, Deal.date_created <= end_date)
            .group_by(Deal.id_client)
        )
        rows = result.all()

    if not rows:
        print("ℹ️ Продаж нет для выбранного периода")
        return ""

    clients = [str(client_id) for client_id, _ in rows]
    sales_counts = [count for _, count in rows]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(clients, sales_counts, color="#4C72B0")
    ax.set_xlabel("ID клиента")
    ax.set_ylabel("Количество продаж")
    ax.set_title(f"Продажи по клиентам ({period_label})")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    os.makedirs("reports/images", exist_ok=True)
    filename = f"reports/images/admin_sales_by_clients_{period_label}.png"
    plt.savefig(filename, dpi=150)
    plt.close()

    print(f"✅ Диаграмма продаж сохранена: {filename}")
    return filename
