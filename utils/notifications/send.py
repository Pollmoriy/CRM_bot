# utils/notifications/send.py

from loader import bot
from database.db import async_session_maker
from database.models import Notification, User, Deal, Task
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

async def create_notification(employee_id: int, title: str, content: str, task_id: Optional[int] = None, deal_id: Optional[int] = None):
    """
    Создаёт запись уведомления в БД и пытается отправить сообщение в Telegram.
    Добавлены логи для диагностики.
    """
    # --- 0) Лог: проверяем входящие параметры ---
    print("🔥 create_notification вызван:")
    print("employee_id =", employee_id)
    print("title =", title)
    print("content =", content)
    print("task_id =", task_id)
    print("deal_id =", deal_id)

    # --- 1) Запись в БД ---
    async with async_session_maker() as session:
        try:
            notif = Notification(
                id_employee=employee_id,
                id_task=task_id,
                id_deal=deal_id,
                title=title,
                content=content
            )
            session.add(notif)
            await session.commit()
            await session.refresh(notif)
            print(f"✅ Уведомление сохранено в БД, id = {notif.id_notification}")
        except SQLAlchemyError as e:
            print(f"[DB ERROR] Ошибка записи в БД: {e}")

    # --- 2) Отправка через Telegram ---
    try:
        async with async_session_maker() as session:
            user = await session.get(User, employee_id)
            tg = getattr(user, "telegram", None) or getattr(user, "telegram_id", None)
            if user and tg:
                await bot.send_message(chat_id=str(tg), text=f"<b>{title}</b>\n\n{content}", parse_mode="HTML")
                print(f"📩 Сообщение Telegram отправлено пользователю {user.full_name} (chat_id={tg})")
            else:
                print(f"[TG WARN] У пользователя нет telegram_id или telegram: {employee_id}")
    except Exception as e:
        print(f"[TG ERROR] Ошибка отправки Telegram-сообщения: {e}")


async def notify_closed_deal(deal: Deal):
    """
    Отправляет уведомления менеджеру и всем сотрудникам, которые были задействованы в сделке.
    Сохраняет уведомления в БД через create_notification.
    """
    # уведомление менеджеру (если назначен)
    if deal.id_manager:
        await create_notification(
            employee_id=deal.id_manager,
            title="Сделка закрыта",
            content=f"✅ Сделка <b>{deal.deal_name}</b> успешно закрыта.",
            deal_id=deal.id_deal
        )

    # уведомляем каждого сотрудника, который имел задачу по этой сделке
    seen_emps = set()
    for task in getattr(deal, "tasks", []):
        if task.id_employee and task.id_employee not in seen_emps:
            seen_emps.add(task.id_employee)
            await create_notification(
                employee_id=task.id_employee,
                title="Сделка закрыта",
                content=f"Сделка <b>{deal.deal_name}</b>, над которой вы работали, закрыта.",
                task_id=task.id_task,
                deal_id=deal.id_deal
            )
