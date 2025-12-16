# handlers/reports/manager_deals_report.py

import os
from datetime import date

import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select
import torch
from handlers.reports.ai_model import tokenizer, model

from database.db import async_session_maker
from database.models import User, Deal, DealStage

# ============================================================
# 🔹 ИИ-МОДЕЛЬ (один раз при старте)
# ============================================================

def generate_ai_recommendations_deals(stats: dict) -> str:
    """
    Генерация профессиональных рекомендаций по сделкам менеджера
    """
    prompt = f"""
    Ты — бизнес-аналитик CRM-системы. Используй только реальные данные конкретного менеджера и его команды. 
    Не придумывай компании, истории, проценты, коэффициенты, оценки, прогнозы или любые числа кроме фактических переданных. 
    Сформулируй 3–4 деловые рекомендации, которые реально помогут менеджеру повысить эффективность работы с текущими сделками. 
    Выдавай только связный текст в виде абзаца, без заголовков, списков, оценок и любых меток.

    Пример правильного ответа:
    Сосредоточьтесь на новых сделках, чтобы своевременно их обработать. Проверяйте сделки в работе регулярно, чтобы выявлять риски и корректировать приоритеты. Анализируйте закрытые сделки, чтобы понять причины успешного и неуспешного завершения, и используйте эти выводы для оптимизации процесса. Поддерживайте команду при решении сложных сделок и равномерно распределяйте задачи.

    Данные менеджера для анализа:
    - Новые: {stats['new']}
    - В работе: {stats['in_progress']}
    - Приостановленные: {stats['on_hold']}
    - Закрытые: {stats['completed']}
    - Всего: {stats['total']}
    """

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.3,
                top_p=0.85,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id
            )

        text = tokenizer.decode(output[0], skip_special_tokens=True)
        text = text.replace(prompt, "").strip()

        # Разделяем на предложения и берём первые 3-4
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
        text = ". ".join(sentences[:4])
        if text:
            text += "."

        if not text:
            return "Рекомендуется активнее отслеживать новые сделки, ускорять выполнение задач и приостанавливать ненужные операции."

        return text

    except Exception as e:
        print(f"⚠️ Ошибка ИИ-аналитики: {e}")
        return "Рекомендуется контролировать новые и приостановленные сделки, оптимизировать работу менеджера и завершать приоритетные сделки."


# ============================================================
# 🔹 CALLBACK: Прогресс сделок менеджера
# ============================================================

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
            return

        # --- Получаем сделки менеджера ---
        result_deals = await session.execute(
            select(Deal).where(Deal.id_manager == manager.id_user)
        )
        deals = result_deals.scalars().all()

        if not deals:
            await query.message.answer("ℹ️ У вас пока нет сделок для отчёта.")
            return

        # --- Подсчёт по этапам ---
        stats_raw = {
            DealStage.new.value: 0,
            DealStage.in_progress.value: 0,
            DealStage.on_hold.value: 0,
            DealStage.completed.value: 0,
        }

        for deal in deals:
            stats_raw[deal.stage.value] += 1

        # --- Преобразуем в удобный формат для ИИ ---
        ai_stats = {
            "new": stats_raw.get("Новая", 0),
            "in_progress": stats_raw.get("В работе", 0),
            "on_hold": stats_raw.get("Приостановлена", 0),
            "completed": stats_raw.get("Закрыта", 0),
            "total": sum(stats_raw.values())
        }

        # --- Построение диаграммы ---
        stages = list(stats_raw.keys())
        counts = list(stats_raw.values())
        colors = {
            "Новая": "#4C72B0",
            "В работе": "#DD8452",
            "Приостановлена": "#8172B2",
            "Закрыта": "#55A868",
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(stages, counts, color=[colors[s] for s in stages], width=0.6)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + 0.05,
                str(int(height)),
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )

        ax.set_title(f"Прогресс сделок менеджера {manager.full_name}\n({date.today()})", fontsize=16, fontweight="bold")
        ax.set_ylabel("Количество сделок", fontsize=12)
        ax.set_xlabel("Этап сделки", fontsize=12)
        ax.set_ylim(0, max(counts)+1)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()

        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/manager_deals_progress.png"
        plt.savefig(filename, dpi=150)
        plt.close()

        # --- Генерация ИИ-рекомендаций ---
        ai_text = generate_ai_recommendations_deals(ai_stats)

        caption = (
            f"📊 Прогресс сделок менеджера {manager.full_name}\n\n"
            f"Статистика сделок:\n"
            f"• Новые: {ai_stats['new']}\n"
            f"• В работе: {ai_stats['in_progress']}\n"
            f"• Приостановленные: {ai_stats['on_hold']}\n"
            f"• Закрытые: {ai_stats['completed']}\n"
            f"• Всего: {ai_stats['total']}\n\n"
            f"🤖 Рекомендации ИИ:\n{ai_text}"
        )

        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print(f"🎯 Отчёт по сделкам отправлен менеджеру: {manager.full_name}")


# ============================================================
# 🔌 Регистрация хендлера
# ============================================================

def register_manager_deals_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_manager_deals_cb_handler,
        lambda c: c.data == "report_manager_deals"
    )
    print("✅ Хендлер report_manager_deals_cb_handler зарегистрирован")
