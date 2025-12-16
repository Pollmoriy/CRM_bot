# handlers/reports/admin_sales_by_clients.py

import os
from datetime import date

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import Deal, Client, DealStage


async def report_admin_sales_cb_handler(query: types.CallbackQuery):
    """💰 Продажи по клиентам (admin)"""
    print(f"📌 Callback report_admin_sales_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по продажам клиентов...")

    async with async_session_maker() as session:
        # --- Получаем сделки с клиентами ---
        result = await session.execute(
            select(
                Client.full_name,
                Deal.stage,
                func.count(Deal.id_deal)
            )
            .join(Deal, Deal.id_client == Client.id_client)
            .group_by(Client.full_name, Deal.stage)
        )

        rows = result.all()

        if not rows:
            await query.message.answer("ℹ️ Нет данных по сделкам клиентов.")
            return

        # --- Агрегация ---
        stats = {}

        for client_name, stage, count in rows:
            if client_name not in stats:
                stats[client_name] = {
                    "total": 0,
                    "closed": 0,
                    "active": 0
                }

            stats[client_name]["total"] += count

            if stage == DealStage.completed.value:
                stats[client_name]["closed"] += count
            else:
                stats[client_name]["active"] += count

        # --- Сортировка по количеству сделок ---
        stats = dict(sorted(
            stats.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        ))

        total_deals = sum(v["total"] for v in stats.values())

        clients = list(stats.keys())
        totals = [stats[c]["total"] for c in clients]

        # --- Диаграмма ---
        fig, ax = plt.subplots(figsize=(12, 7))

        bars = ax.barh(
            clients,
            totals,
            color="#4C72B0"
        )

        max_value = max(totals)
        ax.set_xlim(0, max_value * 1.25)

        # --- Подписи ---
        for i, bar in enumerate(bars):
            data = stats[clients[i]]
            percent = round((data["total"] / total_deals) * 100, 1)

            label = (
                f"{data['total']} сделок | "
                f"Закрыто: {data['closed']} | "
                f"{percent}%"
            )

            width = bar.get_width()

            if width > max_value * 0.6:
                ax.text(
                    width - max_value * 0.03,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    ha="right",
                    va="center",
                    color="white",
                    fontsize=10,
                    fontweight="bold"
                )
            else:
                ax.text(
                    width + max_value * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    ha="left",
                    va="center",
                    fontsize=10
                )

        ax.set_title(
            f"Продажи по клиентам\n(все сделки, на {date.today()})",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel("Количество сделок")
        ax.set_ylabel("Клиенты")
        ax.invert_yaxis()

        ax.grid(axis="x", linestyle="--", alpha=0.4)
        plt.tight_layout()

        # --- Сохранение ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_sales_by_clients.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        # --- Отправка ---
        caption = (
            "💰 Продажи по клиентам\n\n"
            "Диаграмма показывает распределение сделок между клиентами, "
            "долю каждого клиента и количество успешно закрытых сделок.\n\n"
            "Используйте отчёт для выявления ключевых клиентов и оценки "
            "зависимости бизнеса от отдельных заказчиков."
        )

        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )


def register_admin_sales_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_sales_cb_handler,
        lambda c: c.data == "report_admin_sales"
    )
    print("✅ Хендлер report_admin_sales_cb_handler зарегистрирован")
