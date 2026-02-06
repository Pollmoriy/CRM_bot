# handlers/reports/manager_tasks_timeline.py

import os
from datetime import date, timedelta

import torch
import matplotlib.pyplot as plt
from aiogram import types, Dispatcher
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Task, TaskStatus

from handlers.reports.manager_reports import tokenizer, model

# ============================================================
# 🔹 Функция генерации ИИ-рекомендаций
# ============================================================
def generate_ai_recommendations(stats: dict) -> str:
    """
    Генерация профессиональных рекомендаций для менеджера
    на основе статистики задач
    """
    prompt = f"""
    Ты — бизнес-аналитик CRM-системы. Используй только данные команды менеджера.
    Составь 3–4 лаконичные и профессиональные рекомендации для менеджера на основе этих данных.
    Не придумывай компании, проценты или случайные коэффициенты. 
    Выдавай текст связным абзацем без списков и заголовков.
    
    Пример правильного ответа:
    Контролируй просроченные задачи и распределяй их между сотрудниками. 
    Еженедельно анализируй задачи в работе и помогай сотрудникам с приоритетными задачами. 
    Равномерно распределяй новые задачи, чтобы избежать перегрузки. 
    Поощряй сотрудников за своевременное выполнение задач.
    
    Данные команды:
    Создано: {stats['created']}, Завершено: {stats['done']}, Просрочено: {stats['overdue']}, Всего задач: {stats['total']}
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

        # Обрезаем на законченные предложения
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
        text = ". ".join(sentences[:4])
        if text:
            text += "."

        if not text:
            return "Рекомендуется равномерно распределять задачи, контролировать сроки и поддерживать стабильную загрузку команды."

        return text.strip()

    except Exception as e:
        print(f"⚠️ Ошибка ИИ-аналитики: {e}")
        return "Рекомендуется контролировать задачи и оптимизировать распределение нагрузки между сотрудниками."


# ============================================================
# 🔹 Callback: Динамика задач менеджера
# ============================================================
async def report_manager_timeline_cb_handler(query: types.CallbackQuery):
    print(f"📌 Callback report_manager_timeline_cb_handler вызван для Telegram ID: {query.from_user.id}")
    await query.answer("⏳ Формирую динамику задач...")

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == str(query.from_user.id))
        )
        manager = result.scalar_one_or_none()

        if not manager:
            await query.message.answer("❌ Пользователь не найден.")
            return

        print(f"✅ Менеджер: {manager.full_name}")

        days = 30
        today = date.today()
        start_date = today - timedelta(days=days)

        result_tasks = await session.execute(select(Task))
        tasks = result_tasks.scalars().all()
        print(f"ℹ️ Всего задач в БД: {len(tasks)}")

        # Инициализация по дням
        dates = [start_date + timedelta(days=i) for i in range(days + 1)]
        created = {d: 0 for d in dates}
        done = {d: 0 for d in dates}
        overdue = {d: 0 for d in dates}

        for task in tasks:
            if not task.id_employee:
                continue

            result_emp = await session.execute(
                select(User).where(User.id_user == task.id_employee)
            )
            employee = result_emp.scalar_one_or_none()
            if not employee:
                continue

            if employee.id_user != manager.id_user and employee.manager_id != manager.id_user:
                continue

            if task.deadline and start_date <= task.deadline <= today:
                created[task.deadline] += 1

            if task.status == TaskStatus.done and task.date_completed:
                if start_date <= task.date_completed <= today:
                    done[task.date_completed] += 1

            if (
                task.deadline
                and task.deadline < today
                and task.status != TaskStatus.done
                and start_date <= task.deadline <= today
            ):
                overdue[task.deadline] += 1

        if not any(created.values()) and not any(done.values()) and not any(overdue.values()):
            await query.message.answer("ℹ️ Нет данных для отчёта за выбранный период.")
            return

        # Статистика для подписи и ИИ
        stats = {
            "created": sum(created.values()),
            "done": sum(done.values()),
            "overdue": sum(overdue.values()),
            "total": sum(created.values()) + sum(done.values()) + sum(overdue.values())
        }

        # Построение графика
        fig, ax = plt.subplots(figsize=(11, 6))

        x_labels = [d.strftime("%d.%m") for d in dates]

        ax.plot(
            x_labels,
            list(created.values()),
            label="Создано 🟦",
            color="#1565C0",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            list(done.values()),
            label="Завершено 🟩",
            color="#2E7D32",
            linewidth=2.5,
            marker="o"
        )
        ax.plot(
            x_labels,
            list(overdue.values()),
            label="Просрочено 🟥",
            color="#C62828",
            linewidth=2.5,
            marker="o"
        )

        ax.set_title(
            f"📅 Динамика задач менеджера {manager.full_name} за последние {days} дней",
            fontsize=14,
            fontweight="bold"
        )
        ax.set_xlabel("Дата", fontsize=11)
        ax.set_ylabel("Количество задач", fontsize=11)

        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Сохраняем график
        os.makedirs("reports/images", exist_ok=True)
        filename = "reports/images/manager_tasks_timeline.png"
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"✅ Диаграмма сохранена: {filename}")

        # Генерация ИИ-рекомендаций
        ai_text = generate_ai_recommendations(stats)

        # Подпись для отправки
        caption = (
            f"Динамика задач менеджера {manager.full_name} за последние {days} дней\n\n"
            f"Статистика команды:\n"
            f"• Создано: {stats['created']} ({round(stats['created']/stats['total']*100,1) if stats['total'] else 0}%)\n"
            f"• Завершено: {stats['done']} ({round(stats['done']/stats['total']*100,1) if stats['total'] else 0}%)\n"
            f"• Просрочено: {stats['overdue']} ({round(stats['overdue']/stats['total']*100,1) if stats['total'] else 0}%)\n"
            f"• Всего задач: {stats['total']}\n\n"
            #f"🤖 Рекомендации ИИ:\n{ai_text}"
        )

        # Отправка
        await query.message.answer_photo(
            types.InputFile(filename),
            caption=caption
        )

        print(f"🎯 Диаграмма с ИИ-рекомендациями отправлена менеджеру: {manager.full_name}")


# 🔌 Регистрация
def register_manager_timeline_report(dp: Dispatcher):
    dp.register_callback_query_handler(
        report_manager_timeline_cb_handler,
        lambda c: c.data == "report_manager_timeline"
    )
    print("✅ Хендлер report_manager_timeline_cb_handler зарегистрирован")
