import os
from datetime import date

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import Client, Deal, DealStage


async def report_admin_sales_cb_handler(query: types.CallbackQuery):
    """💰 Активность клиентов по сделкам (админ)"""
    print(f"📌 Callback report_admin_sales_cb_handler: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по клиентам...")

    async with async_session_maker() as session:
        result = await session.execute(select(Client))
        clients = result.scalars().all()

        if not clients:
            await query.message.answer("ℹ️ Клиенты отсутствуют.")
            return

        stats = {}

        for client in clients:
            result_deals = await session.execute(
                select(Deal).where(Deal.id_client == client.id_client)
            )
            deals = result_deals.scalars().all()

            if not deals:
                continue

            total = len(deals)
            closed = sum(1 for d in deals if d.stage == DealStage.completed.value)
            active = total - closed
            success_rate = round((closed / total) * 100, 1) if total else 0

            stats[client.full_name] = {
                "total": total,
                "closed": closed,
                "active": active,
                "success": success_rate,
            }

        if not stats:
            await query.message.answer("ℹ️ Нет данных по сделкам клиентов.")
            return

        # --- Сортировка по количеству сделок ---
        stats = dict(sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True))

        client_names = list(stats.keys())
        totals = [v["total"] for v in stats.values()]

        # --- Диаграмма ---
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(client_names, totals, color="#4C72B0")

        max_value = max(totals)
        ax.set_xlim(0, max_value * 1.25)  # запас справа

        for i, bar in enumerate(bars):
            data = list(stats.values())[i]
            text = (
                f"Всего: {data['total']} | "
                f"Закрыто: {data['closed']} | "
                f"Успех: {data['success']}%"
            )

            width = bar.get_width()

            # Если столбец длинный — текст внутри
            if width > max_value * 0.6:
                ax.text(
                    width - max_value * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    text,
                    va="center",
                    ha="right",
                    fontsize=10,
                    color="white",
                    fontweight="bold"
                )
            else:
                # Иначе — снаружи
                ax.text(
                    width + max_value * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    text,
                    va="center",
                    ha="left",
                    fontsize=10
                )

        ax.set_xlabel("Количество сделок", fontsize=12)
        ax.set_title(
            f"Активность клиентов по сделкам\n(по состоянию на {date.today()})",
            fontsize=14,
            fontweight="bold"
        )
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        plt.tight_layout()

        # --- Сохранение ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_clients_activity.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        await query.message.answer_photo(
            types.InputFile(filename),
            caption=(
                "💰 Активность клиентов\n"
                "Показано общее количество сделок, число закрытых и процент успешных."
            )
        )


def register_admin_sales_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_sales_cb_handler,
        lambda c: c.data == "report_admin_sales"
    )
    print("✅ Хендлер report_admin_sales_cb_handler зарегистрирован")
