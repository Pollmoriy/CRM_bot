# handlers/reports/admin_deals_report.py

import os
from datetime import date
import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select, func

from database.db import async_session_maker
from database.models import User, Deal, DealStage


async def report_admin_deals_cb_handler(query: types.CallbackQuery):
    print(f"📌 Callback report_admin_deals_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт по сделкам всех сотрудников...")

    async with async_session_maker() as session:
        # --- Получаем всех менеджеров ---
        result_users = await session.execute(select(User).where(User.role == "manager"))
        managers = result_users.scalars().all()
        print(f"ℹ️ Найдено менеджеров: {len(managers)}")

        if not managers:
            await query.message.answer("❌ Нет менеджеров в системе.")
            return

        # --- Собираем сделки ---
        stats = {
            DealStage.new.value: 0,
            DealStage.in_progress.value: 0,
            DealStage.on_hold.value: 0,
            DealStage.completed.value: 0,
        }

        total_deals = 0

        for manager in managers:
            print(f"ℹ️ Менеджер: {manager.full_name}, ID: {manager.id_user}")
            result_deals = await session.execute(select(Deal).where(Deal.id_manager == manager.id_user))
            deals = result_deals.scalars().all()
            print(f"ℹ️ Сделок у менеджера {manager.full_name}: {len(deals)}")

            for deal in deals:
                print(f"   ⚡ Сделка ID {deal.id_deal}, Этап: {deal.stage}")
                stats[deal.stage.value] += 1
                total_deals += 1

        print(f"ℹ️ Общая статистика сделок: {stats}")
        print(f"ℹ️ Общее количество сделок: {total_deals}")

        if total_deals == 0:
            await query.message.answer("ℹ️ Сделок пока нет для отображения.")
            return

        # --- Диаграмма ---
        stages = list(stats.keys())
        counts = list(stats.values())
        percentages = [round(c / total_deals * 100, 1) for c in counts]

        colors = {
            "Новая": "#4C72B0",
            "В работе": "#DD8452",
            "Приостановлена": "#8172B2",
            "Закрыта": "#55A868",
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            stages,
            counts,
            color=[colors[s] for s in stages],
            width=0.6
        )

        # Подписи над столбцами с количеством и процентом
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

        ax.set_title(
            f"Прогресс сделок всех сотрудников\n({date.today()})",
            fontsize=16,
            fontweight="bold"
        )
        ax.set_ylabel("Количество сделок", fontsize=12)
        ax.set_xlabel("Этап сделки", fontsize=12)

        ax.set_ylim(0, max(counts) + 3)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        # --- Сохранение ---
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/admin_deals_progress.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        # --- Отправка ---
        caption = (
            f"📈 Прогресс сделок всех сотрудников\n\n"
            f"Общее количество сделок: {total_deals}\n"
            f"• Новые: {stats['Новая']} ({percentages[0]}%)\n"
            f"• В работе: {stats['В работе']} ({percentages[1]}%)\n"
            f"• Приостановленные: {stats['Приостановлена']} ({percentages[2]}%)\n"
            f"• Закрытые: {stats['Закрыта']} ({percentages[3]}%)\n\n"
            f"Используйте график для оценки прогресса сделок и выявления узких мест в работе команды."
        )

        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print(f"🎯 Отчёт по сделкам всех сотрудников отправлен администратору.")


# 🔌 Регистрация
def register_admin_deals_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_admin_deals_cb_handler,
        lambda c: c.data == "report_admin_deals"
    )
    print("✅ Хендлер report_admin_deals_cb_handler зарегистрирован")
