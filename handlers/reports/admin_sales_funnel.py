# handlers/reports/admin_sales_funnel.py
import os
from collections import OrderedDict

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import Deal, DealStage


async def report_admin_funnel_cb_handler(query: types.CallbackQuery):
    await query.answer("⏳ Формирую воронку продаж...")

    async with async_session_maker() as session:
        result = await session.execute(
            select(Deal.stage, func.count(Deal.id_deal))
            .group_by(Deal.stage)
        )
        rows = result.all()

    if not rows:
        await query.message.answer("ℹ️ Сделки отсутствуют.")
        return

    raw = {}
    for stage, count in rows:
        name = stage.value if hasattr(stage, "value") else stage
        raw[name] = count

    stages = OrderedDict([
        ("Новая", raw.get("Новая", 0)),
        ("В работе", raw.get("В работе", 0)),
        ("Приостановлена", raw.get("Приостановлена", 0)),
        ("Закрыта", raw.get("Закрыта", 0)),
    ])

    values = list(stages.values())
    labels = list(stages.keys())

    total = values[0]
    if total == 0:
        await query.message.answer("ℹ️ Недостаточно данных для анализа воронки.")
        return

    # --- ФИКСИРОВАННАЯ ФОРМА ВОРОНКИ ---
    widths = [1.0, 0.78, 0.56, 0.38]
    colors = ["#E3F2FD", "#90CAF9", "#64B5F6", "#1E88E5"]

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, (label, value, width) in enumerate(zip(labels, values, widths)):
        left = 0.5 - width / 2

        ax.barh(
            y=i,
            width=width,
            left=left,
            height=1.0,  # без зазоров
            color=colors[i],
            linewidth=0  # без обводки
        )

        ax.text(
            0.5,
            i,
            f"{label}\n{value} сделок",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#0D47A1"
        )

    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.invert_yaxis()

    ax.set_title(
        "Воронка продаж (все сотрудники)",
        fontsize=15,
        fontweight="bold",
        pad=20
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    os.makedirs("reports/images", exist_ok=True)
    filename = "reports/images/admin_sales_funnel.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    # --- КОНВЕРСИИ ---
    conversion_lines = []

    for i in range(len(values) - 1):
        if values[i] > 0:
            conv = round(values[i + 1] / values[i] * 100, 1)
            conversion_lines.append(
                f"• {labels[i]} → {labels[i+1]}: {conv}%"
            )

    overall_conv = round(values[-1] / values[0] * 100, 1)

    caption = (
        "🪣 *Воронка продаж*\n\n"
        "Схематичное распределение сделок по этапам.\n"
        "Форма воронки фиксированная, значения отражают реальные данные.\n\n"
        "*Конверсия между этапами:*\n"
        + "\n".join(conversion_lines)
        + f"\n\n*Общая конверсия в закрытие:* {overall_conv}%"
    )

    await query.message.answer_photo(
        types.InputFile(filename),
        caption=caption,
        parse_mode="Markdown"
    )


def register_admin_funnel_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_funnel_cb_handler,
        lambda c: c.data == "report_admin_funnel"
    )
