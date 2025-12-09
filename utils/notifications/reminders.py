# utils/notifications/reminders.py
from datetime import date
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from database.db import async_session_maker
from database.models import Task, Deal
from utils.notifications.send import create_notification, notify_closed_deal
from utils.notifications.helpers import format_task_deadline, format_task_overdue


async def _notification_exists_for_task(session, task_id: int, title: str, same_day: bool = False):
    """
    Проверяет, есть ли в БД уведомление с таким task_id и title.
    same_day=True — ищем уведомление, созданное сегодня.
    """
    if same_day:
        sql = text("""
            SELECT COUNT(*) 
            FROM notifications
            WHERE id_task = :task_id
              AND title = :title
              AND DATE(created_at) = :today
        """)
        res = await session.execute(sql, {
            "task_id": task_id,
            "title": title,
            "today": date.today()
        })
    else:
        sql = text("""
            SELECT COUNT(*) 
            FROM notifications
            WHERE id_task = :task_id
              AND title = :title
        """)
        res = await session.execute(sql, {
            "task_id": task_id,
            "title": title
        })

    row = res.fetchone()
    if not row:
        return False

    # row — это tuple, берём row[0]
    return int(row[0]) > 0



async def check_task_reminders():
    """
    Создаёт уведомления для задач:
    - напоминания за 7/3/1 дней (не чаще одного раза в день)
    - просроченные задачи (только один раз)
    """
    today = date.today()
    upcoming_days = {1, 3, 7}

    async with async_session_maker() as session:
        result = await session.execute(
            select(Task)
            .options(
                selectinload(Task.employee),
                selectinload(Task.deal).selectinload(Deal.manager)
            )
            .where(Task.status != 'done')
        )
        tasks = result.scalars().all()

    print(f"🔔 Проверка напоминаний: найдено {len(tasks)} активных задач")

    for task in tasks:
        task_id = task.id_task

        if not task.deadline:
            print(f"⚠️ Пропущена задача {task_id}: нет дедлайна")
            continue
        if not task.employee:
            print(f"⚠️ Пропущена задача {task_id}: нет сотрудника")
            continue

        days_left = (task.deadline - today).days
        print(f"ℹ️ Задача {task_id}: '{task.task_name}', дедлайн через {days_left} дней")

        # --- Напоминание о приближении (1/3/7 дней) ---
        if days_left in upcoming_days:

            async with async_session_maker() as session:
                already_today = await _notification_exists_for_task(
                    session, task_id, "Напоминание о задаче", same_day=True
                )

            if not already_today:
                print(f"📩 Создаём напоминание сотруднику {task.employee.full_name}")
                await create_notification(
                    employee_id=task.id_employee,
                    title="Напоминание о задаче",
                    content=format_task_deadline(task.task_name, task.deadline),
                    task_id=task.id_task,
                    deal_id=task.id_deal
                )
            else:
                print(f"ℹ️ Напоминание по задаче {task_id} сегодня уже отправлялось — пропуск")

        # --- Просроченная ---
        elif days_left < 0:

            async with async_session_maker() as session:
                exists = await _notification_exists_for_task(
                    session, task_id, "Просроченная задача", same_day=False
                )

            if exists:
                print(f"ℹ️ Уведомление о просрочке задачи {task_id} уже существует — пропуск")
            else:
                overdue_days = abs(days_left)
                print(f"⚠️ Просрочка: задача {task.task_name}, сотрудник: {task.employee.full_name}")

                content = format_task_overdue(task.task_name, task.deadline)
                content += f"\n\n⌛ Просрочена на {overdue_days} д."

                # уведомление сотруднику
                await create_notification(
                    employee_id=task.id_employee,
                    title="Просроченная задача",
                    content=content,
                    task_id=task.id_task,
                    deal_id=task.id_deal
                )

                # уведомление менеджеру
                if task.deal and task.deal.manager:
                    print(f"📩 Уведомляем менеджера {task.deal.manager.full_name}")
                    await create_notification(
                        employee_id=task.deal.id_manager,
                        title="Просроченная задача у сотрудника",
                        content=(
                            f"Сотрудник <b>{task.employee.full_name}</b> просрочил задачу '{task.task_name}'. "
                            f"Дедлайн был {task.deadline.strftime('%d.%m.%Y')}, "
                            f"просрочена на {overdue_days} д."
                        ),
                        task_id=task.id_task,
                        deal_id=task.id_deal
                    )



async def check_closed_deals():
    """
    Проверяет сделки в стадии 'Закрыта' и отправляет уведомления, если они ещё не отправлялись.
    """
    async with async_session_maker() as session:
        result = await session.execute(select(Deal).where(Deal.stage == "Закрыта"))
        deals = result.scalars().all()

    print(f"🔔 Проверка закрытых сделок: найдено {len(deals)}")

    for deal in deals:
        async with async_session_maker() as session:
            r = await session.execute(text("""
                SELECT COUNT(*) 
                FROM notifications 
                WHERE id_deal = :id AND title = 'Сделка закрыта'
            """), {"id": deal.id_deal})
            row = r.fetchone()

        if row and row[0] > 0:
            print(f"ℹ️ По сделке '{deal.deal_name}' уведомление уже есть — пропуск")
            continue

        print(f"📩 Отправляем уведомление по сделке '{deal.deal_name}'")
        await notify_closed_deal(deal)
