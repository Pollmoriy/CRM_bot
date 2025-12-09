# utils/notifications/helpers.py

from datetime import date

def format_task_deadline(task_name: str, deadline: date) -> str:
    if not deadline:
        return f"Задача <b>{task_name}</b> без установленного дедлайна."
    return f"Задача <b>{task_name}</b> должна быть выполнена до <b>{deadline.strftime('%d.%m.%Y')}</b>."

def format_task_overdue(task_name: str, deadline: date) -> str:
    return f"❗ Задача <b>{task_name}</b> просрочена! Дедлайн был {deadline.strftime('%d.%m.%Y')}."

def format_new_task(task_name: str, deal_name: str) -> str:
    return f"📌 Новая задача <b>{task_name}</b> для сделки <b>{deal_name}</b>."

def format_deal_closed(deal_name: str) -> str:
    return f"✅ Сделка <b>{deal_name}</b> закрыта."
