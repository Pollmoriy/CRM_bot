# handlers/reports/manager_reports.py

import os
from datetime import date

import torch
import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select
from handlers.reports.ai_model import tokenizer, model

from database.db import async_session_maker
from database.models import User, Task, TaskStatus




# ============================================================
# 🔹 ФУНКЦИЯ ИИ-РЕКОМЕНДАЦИЙ (БЕЗ pipeline)
# ============================================================

def generate_ai_recommendations(stats: dict) -> str:
    """
    Генерация профессиональных рекомендаций для менеджера.
    Ответ — лаконичный текст, 3–4 законченные рекомендации в виде обычных предложений.
    """

    prompt = f"""
    Ты — бизнес-аналитик CRM-системы. Используй только данные команды менеджера, 
    не придумывай компании, истории или общие фразы. Сформулируй 3–4 деловые рекомендации, 
    которые реально помогут повысить эффективность команды. Выдавай только текст в виде связного абзаца, без заголовков, списков, оценок и любых меток.

    Пример правильного ответа:
    Контролируй просроченные задачи и распределяй их между сотрудниками. Еженедельно анализируй задачи в работе и помогай сотрудникам с приоритетными задачами. Равномерно распределяй новые задачи, чтобы избежать перегрузки. Поощряй сотрудников за своевременное выполнение задач.

    Данные команды для анализа:
    Выполнено: {stats['done']}, В работе: {stats['in_progress']}, Новые: {stats['new']}, Просроченные: {stats['overdue']}, Всего задач: {stats['total']}
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
                max_new_tokens=200,  # увеличиваем для полноты предложений
                do_sample=True,
                temperature=0.3,
                top_p=0.85,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id
            )

        text = tokenizer.decode(output[0], skip_special_tokens=True)
        # убираем повторение промта
        text = text.replace(prompt, "").strip()

        # делим на предложения и обрезаем короткие обрывки
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 15]
        text = ". ".join(sentences[:4])
        if text and not text.endswith("."):
            text += "."

        # если текст пустой, вернуть стандартный
        if not text:
            return (
                "Равномерно распределяй задачи между сотрудниками, контролируй сроки выполнения и поддерживай стабильную загрузку команды."
            )

        return text.strip()

    except Exception as e:
        print(f"⚠️ Ошибка ИИ-аналитики: {e}")
        return (
            "Рекомендуется усилить контроль сроков выполнения задач и оптимизировать распределение нагрузки между сотрудниками."
        )



# ============================================================
# 🔹 ХЕНДЛЕР ОТЧЁТА ПО ЗАДАЧАМ (ДЛЯ МЕНЕДЖЕРА)
# ============================================================

async def report_manager_tasks_cb_handler(query: types.CallbackQuery):
    print(f"📌 Callback report_manager_tasks_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую отчёт...")

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == str(query.from_user.id))
        )
        manager = result.scalar_one_or_none()

        if not manager:
            await query.message.answer("❌ Пользователь не найден.")
            return

        result_tasks = await session.execute(select(Task))
        tasks = result_tasks.scalars().all()

        data = {}

        for task in tasks:
            if not task.id_employee:
                continue

            result_emp = await session.execute(
                select(User).where(User.id_user == task.id_employee)
            )
            employee = result_emp.scalar_one_or_none()
            if not employee:
                continue

            if employee.manager_id != manager.id_user:
                continue

            if employee.full_name not in data:
                data[employee.full_name] = {
                    TaskStatus.new: 0,
                    TaskStatus.in_progress: 0,
                    TaskStatus.done: 0,
                    TaskStatus.overdue: 0,
                }

            data[employee.full_name][TaskStatus(task.status)] += 1

        if not data:
            await query.message.answer("ℹ️ Нет данных для отчёта.")
            return


        # ====================================================
        # 🔹 СТАТИСТИКА
        # ====================================================

        employees_count = len(data)
        total_tasks = sum(sum(v.values()) for v in data.values())

        avg_done = round(sum(v[TaskStatus.done] for v in data.values()) / employees_count, 2)
        avg_in_progress = round(sum(v[TaskStatus.in_progress] for v in data.values()) / employees_count, 2)
        avg_new = round(sum(v[TaskStatus.new] for v in data.values()) / employees_count, 2)
        avg_overdue = round(sum(v[TaskStatus.overdue] for v in data.values()) / employees_count, 2)

        stats = {
            "done": avg_done,
            "in_progress": avg_in_progress,
            "new": avg_new,
            "overdue": avg_overdue,
            "total": total_tasks
        }


        # ====================================================
        # 🔹 ДИАГРАММА
        # ====================================================

        employees = list(data.keys())
        statuses = [
            TaskStatus.done,
            TaskStatus.in_progress,
            TaskStatus.new,
            TaskStatus.overdue
        ]

        colors = {
            TaskStatus.done: "#2E7D32",
            TaskStatus.in_progress: "#1565C0",
            TaskStatus.new: "#F9A825",
            TaskStatus.overdue: "#C62828",
        }

        fig, ax = plt.subplots(figsize=(11, 6))
        bottoms = [0] * len(employees)

        for status in statuses:
            counts = [data[e][status] for e in employees]
            ax.barh(
                employees,
                counts,
                left=bottoms,
                color=colors[status],
                label=status.name.replace("_", " ").title(),
            )
            bottoms = [bottoms[i] + counts[i] for i in range(len(employees))]

        ax.set_xlabel("Количество задач")
        ax.set_title(
            f"Нагрузка и эффективность сотрудников ({date.today()})",
            fontweight="bold"
        )
        ax.invert_yaxis()
        ax.legend()
        plt.tight_layout()

        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/manager_tasks_report.png"
        plt.savefig(filename, dpi=150)
        plt.close()


        # ====================================================
        # 🔹 ИИ-РЕКОМЕНДАЦИИ
        # ====================================================

        #ai_text = generate_ai_recommendations(stats)

        caption = (
            "📊 Нагрузка и эффективность сотрудников\n\n"
            f"Средняя загрузка команды:\n"
            f"• Выполнено: {avg_done}\n"
            f"• В работе: {avg_in_progress}\n"
            f"• Новые: {avg_new}\n"
            f"• Просроченные: {avg_overdue}\n\n"
            #f"🤖 Рекомендации ИИ:\n{ai_text}"
        )

        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print(f"🎯 Отчёт с ИИ-рекомендациями отправлен: {manager.full_name}")


# ============================================================
# 🔹 РЕГИСТРАЦИЯ ХЕНДЛЕРА
# ============================================================

def register_manager_reports(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_manager_tasks_cb_handler,
        lambda c: c.data == "report_manager_tasks",
    )

    print("✅ Хендлер report_manager_tasks_cb_handler зарегистрирован")
