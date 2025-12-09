# utils/notifications/send_closed_deal.py

from loader import bot
from database.db import async_session_maker
from database.models import Deal, Task, User
from utils.notifications.send import create_notification


async def notify_closed_deal(deal: Deal):
    """
    Отправляет уведомления менеджеру и всем сотрудникам, которые работали над сделкой.
    Создаёт записи в БД и отправляет Telegram-сообщения.
    """
    print(f"🔥 notify_closed_deal вызван для сделки: {deal.deal_name}")

    async with async_session_maker() as session:
        # --- Менеджер ---
        if deal.id_manager:
            print(f"📩 Отправляем уведомление менеджеру (id={deal.id_manager})")
            await create_notification(
                employee_id=deal.id_manager,
                title="Сделка закрыта",
                content=f"✅ Сделка <b>{deal.deal_name}</b> успешно закрыта.",
                deal_id=deal.id_deal
            )

        # --- Сотрудники, которые работали над задачами по этой сделке ---
        result = await session.execute(
            select(Task).where(Task.id_deal == deal.id_deal)
        )
        tasks = result.scalars().all()

        seen_employees = set()
        for task in tasks:
            if task.id_employee and task.id_employee not in seen_employees:
                seen_employees.add(task.id_employee)
                print(f"📩 Отправляем уведомление сотруднику (id={task.id_employee})")
                await create_notification(
                    employee_id=task.id_employee,
                    title="Сделка закрыта",
                    content=f"Сделка <b>{deal.deal_name}</b>, над которой вы работали, закрыта.",
                    task_id=task.id_task,
                    deal_id=deal.id_deal
                )

    print(f"✅ Уведомления о закрытой сделке '{deal.deal_name}' отправлены.\n")
