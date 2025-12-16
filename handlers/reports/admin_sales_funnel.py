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
        # --- Получаем количество сделок по этапам ---
        result = await session.execute(
            select(Deal.stage, func.count(Deal.id_deal)).group_by(Deal.stage)
        )
        rows = result.all()

    if not rows:
        await query.message.answer("ℹ️ Сделки отсутствуют.")
        return

    # --- Отладка: показываем сырые данные ---
    print("⚡ DEBUG: raw rows from DB:")
    for stage, count in rows:
        print(f"   stage: {stage}, count: {count}")

    raw = {}
    for stage, count in rows:
        name = stage.value if hasattr(stage, "value") else stage
        raw[name] = count

    # --- Упорядочиваем этапы воронки ---
    stages = OrderedDict([
        ("Новая", raw.get("Новая", 0)),
        ("В работе", raw.get("В работе", 0)),
        ("Приостановлена", raw.get("Приостановлена", 0)),
        ("Закрыта", raw.get("Закрыта", 0)),
    ])

    values = list(stages.values())
    labels = list(stages.keys())
    total_deals = sum(values)

    # --- Отладка ---
    print(f"⚡ DEBUG: stages OrderedDict: {stages}")
    print(f"⚡ DEBUG: total_deals: {total_deals}")

    if total_deals == 0:
        await query.message.answer("ℹ️ Недостаточно данных для анализа воронки.")
        return

    # --- Фиксированная форма воронки ---
    widths = [1.0, 0.78, 0.56, 0.38]
    # прежний блок цветов заменяем на градиент синего
    colors = ["#E3F2FD", "#90CAF9", "#64B5F6", "#1E88E5"]  # градиент синего

    fig, ax = plt.subplots(figsize=(8, 6))

    for i, (label, value, width) in enumerate(zip(labels, values, widths)):
        left = 0.5 - width / 2
        ax.barh(
            y=i,
            width=width,
            left=left,
            height=1.0,
            color=colors[i],
            linewidth=0
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
    ax.set_title("Воронка продаж (все сотрудники)", fontsize=15, fontweight="bold", pad=20)
    for spine in ax.spines.values():
        spine.set_visible(False)

    os.makedirs("reports/images", exist_ok=True)
    filename = "reports/images/admin_sales_funnel.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

    # --- Конверсии ---
    conversion_lines = []
    prev_total = total_deals
    for i in range(len(values) - 1):
        curr_val = values[i + 1]
        conv = round(curr_val / prev_total * 100, 1) if prev_total > 0 else 0
        conversion_lines.append(f"• {labels[i]} → {labels[i+1]}: {conv}%")
        print(f"⚡ DEBUG: {labels[i]} → {labels[i+1]} | prev_total={prev_total}, curr_val={curr_val}, conv={conv}%")
        prev_total = values[i + 1] if values[i + 1] > 0 else 1  # избегаем деления на 0

    overall_conv = round(stages["Закрыта"] / total_deals * 100, 1)
    print(f"⚡ DEBUG: overall conversion: {overall_conv}")

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
    print("✅ Хендлер report_admin_funnel_cb_handler зарегистрирован")
