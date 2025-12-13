# handlers/reports/manager_deals_report.py

import os
from datetime import date

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Deal, DealStage


# 🎯 CALLBACK: Прогресс сделок менеджера
async def report_manager_deals_cb_handler(query: types.CallbackQuery):
    print(f"📌 Callback report_manager_deals_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по сделкам...")

    async with async_session_maker() as session:
        # --- Получаем менеджера ---
        result_user = await session.execute(
            select(User).where(User.telegram_id == str(query.from_user.id))
        )
        manager = result_user.scalar_one_or_none()

        if not manager:
            await query.message.answer("❌ Пользователь не найден.")
            print("❌ Менеджер не найден")
            return

        print(f"✅ Менеджер: {manager.full_name}")

        # --- Получаем сделки менеджера ---
        result_deals = await session.execute(
            select(Deal).where(Deal.id_manager == manager.id_user)
        )
        deals = result_deals.scalars().all()

        print(f"ℹ️ Найдено сделок: {len(deals)}")

        if not deals:
            await query.message.answer("ℹ️ У вас пока нет сделок для отчёта.")
            return

        # --- Подсчёт по этапам ---
        stats = {
            DealStage.new.value: 0,
            DealStage.in_progress.value: 0,
            DealStage.on_hold.value: 0,
            DealStage.completed.value: 0,
        }

        for deal in deals:
            stats[deal.stage.value] += 1

        print(f"ℹ️ Статистика сделок: {stats}")

        # --- Построение диаграммы ---
        stages = list(stats.keys())
        counts = list(stats.values())

        colors = {
            "Новая": "#4C72B0",
            "В работе": "#DD8452",
            "Приостановлена": "#8172B2",
            "Закрыта": "#55A868",
        }

        fig, ax = plt.subplots(figsize=(8, 6))

        bars = ax.bar(
            stages,
            counts,
            color=[colors[s] for s in stages],
            width=0.6
        )

        # Подписи над столбцами
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.05,
                str(int(height)),
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )

        ax.set_title(
            f"Прогресс сделок менеджера\n({date.today()})",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_ylabel("Количество сделок", fontsize=11)
        ax.set_xlabel("Этап сделки", fontsize=11)

        ax.set_ylim(0, max(counts) + 1)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        # --- Сохранение ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/manager_deals_progress.png"

        plt.savefig(filename, dpi=150)
        plt.close()

        print(f"✅ Диаграмма сохранена: {filename}")

        # --- Отправка ---
        await query.message.answer_photo(
            types.InputFile(filename),
            caption="📈 Прогресс ваших сделок"
        )

        print(f"🎯 Отчёт по сделкам отправлен менеджеру: {manager.full_name}")


# 🔌 Регистрация
def register_manager_deals_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_manager_deals_cb_handler,
        lambda c: c.data == "report_manager_deals"
    )
    print("✅ Хендлер report_manager_deals_cb_handler зарегистрирован")
