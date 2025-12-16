# handlers/reports/admin_deals_report.py

import os
from datetime import date
import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Deal, DealStage

STAGE_COLORS = {
    "Новая": "#4C72B0",
    "В работе": "#8C6BB1",
    "Приостановлена": "#D9A066",
    "Закрыта": "#55A868",
}


async def report_admin_deals_cb_handler(query: types.CallbackQuery):
    print(f"📌 Callback report_admin_deals_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по сделкам всех сотрудников...")

    async with async_session_maker() as session:
        result_users = await session.execute(select(User).where(User.role == "manager"))
        managers = result_users.scalars().all()
        print(f"ℹ️ Найдено менеджеров: {len(managers)}")

        if not managers:
            await query.message.answer("❌ Нет менеджеров в системе.")
            return

        stats = {s.value: 0 for s in DealStage}
        total_deals = 0

        for manager in managers:
            result_deals = await session.execute(select(Deal).where(Deal.id_manager == manager.id_user))
            deals = result_deals.scalars().all()
            print(f"ℹ️ Менеджер {manager.full_name}, ID {manager.id_user}, сделки: {len(deals)}")
            for deal in deals:
                stage_val = deal.stage.value if isinstance(deal.stage, DealStage) else deal.stage
                print(f"   ⚡ Сделка ID {deal.id_deal}, stage: {stage_val}")
                if stage_val in stats:
                    stats[stage_val] += 1
                    total_deals += 1

        print(f"ℹ️ Общая статистика сделок: {stats}")
        print(f"ℹ️ Общее количество сделок: {total_deals}")

        if total_deals == 0:
            await query.message.answer("ℹ️ Сделок пока нет для отображения.")
            return

        stages = list(stats.keys())
        counts = list(stats.values())
        percentages = [round(c / total_deals * 100, 1) for c in counts]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(stages, counts, color=[STAGE_COLORS[s] for s in stages], width=0.6)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.05,
                f"{int(height)} ({percentages[i]}%)",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )

        ax.set_title(f"Прогресс сделок всех сотрудников\n({date.today()})", fontsize=16, fontweight="bold")
        ax.set_ylabel("Количество сделок", fontsize=12)
        ax.set_xlabel("Этап сделки", fontsize=12)
        ax.set_ylim(0, max(counts) + 3)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()

        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_deals_progress.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        caption = (
            f"📈 Прогресс сделок всех сотрудников\n\n"
            f"Общее количество сделок: {total_deals}\n"
            + "\n".join([f"• {stages[i]}: {counts[i]} ({percentages[i]}%)" for i in range(len(stages))])
            + "\n\nИспользуйте график для оценки прогресса сделок и выявления узких мест в работе команды."
        )

        await query.message.answer_photo(types.InputFile(filename), caption=caption)
        print(f"🎯 Отчёт по сделкам всех сотрудников отправлен администратору.")


def register_admin_deals_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_deals_cb_handler,
        lambda c: c.data == "report_admin_deals"
    )
    print("✅ Хендлер report_admin_deals_cb_handler зарегистрирован")
