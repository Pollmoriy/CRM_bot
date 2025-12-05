# handlers/deals/view_deals.py

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, safe_answer
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import handlers.deals.history
import handlers.deals.progress
from database.db import async_session_maker
from database.models import Deal, User, Task, DealStage
from keyboards.deals_pages_kb import top_deals_kb, deals_nav_kb
from handlers.deals.tasks import show_tasks  # импорт функции отображения задач

DEALS_PER_PAGE = 5

# ------------------------------
# Загрузка сделок с учётом роли, поиска и фильтров
# ------------------------------
async def load_deals(user: User, search_name: str = "", filter_by: str = ""):
    conditions = []

    if search_name:
        conditions.append(Deal.deal_name.ilike(f"%{search_name}%"))

    if filter_by:
        try:
            f_type, f_val = filter_by.split("|", 1)
        except:
            f_type, f_val = "", ""

        if f_type == "stage":
            # Используем значения на русском, как в БД
            stage_value = next((e.value for e in DealStage if e.name == f_val), None)
            if stage_value:
                conditions.append(Deal.stage == stage_value)
        elif f_type == "date":
            now = datetime.now()
            if f_val == "today":
                date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif f_val == "week":
                date_from = now - timedelta(days=7)
            elif f_val == "month":
                date_from = now - timedelta(days=30)
            else:
                date_from = None
            if date_from:
                conditions.append(Deal.date_created >= date_from)
        elif f_type == "manager":
            try:
                manager_id = int(f_val)
                conditions.append(Deal.id_manager == manager_id)
            except:
                pass

    async with async_session_maker() as session:
        role = user.role.value if user and user.role else "employee"
        base_query = select(Deal).options(selectinload(Deal.tasks))

        if role == "manager":
            base_query = base_query.where(Deal.id_manager == user.id_user)
        elif role == "employee":
            base_query = base_query.join(Task).where(Task.id_employee == user.id_user)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        result = await session.execute(base_query)
        return result.scalars().all()


# ------------------------------
# Формирование клавиатуры списка сделок
# ------------------------------
def get_deals_keyboard(deals, page: int, search_name: str, filter_by: str):
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * DEALS_PER_PAGE
    end = start + DEALS_PER_PAGE

    for deal in deals[start:end]:
        kb.add(
            InlineKeyboardButton(
                text=f"{deal.deal_name} (ID {deal.id_deal})",
                callback_data=f"deal_detail_{deal.id_deal}"
            )
        )

    has_next = end < len(deals)
    nav_kb = deals_nav_kb(page, has_next, search_name, filter_by)
    for row in nav_kb.inline_keyboard:
        kb.row(*row)

    top_kb = top_deals_kb()
    for row in top_kb.inline_keyboard:
        kb.row(*row)

    return kb


# ------------------------------
# Отображение сделок
# ------------------------------
async def show_deals(message_or_callback, page: int = 1, search_name: str = "", filter_by: str = ""):
    message = message_or_callback.message if isinstance(message_or_callback, types.CallbackQuery) else message_or_callback
    telegram_id = str(message.chat.id)

    async with async_session_maker() as session:
        user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_q.scalar_one_or_none()

    if not user:
        await message.answer("⚠️ Пользователь не найден.")
        return

    deals = await load_deals(user, search_name, filter_by)

    if not deals:
        try:
            await message.edit_text("📁 Сделок не найдено по заданным критериям.")
        except:
            await message.answer("📁 Сделок не найдено по заданным критериям.")
        return

    kb = get_deals_keyboard(deals, page, search_name, filter_by)
    try:
        await message.edit_text("📁 Список сделок:", reply_markup=kb)
    except:
        await message.answer("📁 Список сделок:", reply_markup=kb)


# ------------------------------
# Детали сделки
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_detail_"))
async def show_deal_detail(callback: types.CallbackQuery):
    await safe_answer(callback)
    deal_id = int(callback.data.split("_")[-1])
    telegram_id = str(callback.from_user.id)

    async with async_session_maker() as session:
        deal = await session.get(
            Deal,
            deal_id,
            options=[selectinload(Deal.client), selectinload(Deal.manager), selectinload(Deal.tasks)]
        )
        user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_q.scalar_one_or_none()

    if not deal:
        await callback.message.edit_text("⚠️ Сделка не найдена.")
        return

    num_tasks = len(deal.tasks)
    completed_tasks = len([t for t in deal.tasks if getattr(t.status, "name", None) == "done"])
    progress_percent = int(completed_tasks / num_tasks * 100) if num_tasks else 0

    stage_display = deal.stage

    text = (
        f"<b>Сделка:</b> {deal.deal_name}\n"
        f"<b>Клиент:</b> {deal.client.full_name if deal.client else '—'}\n"
        f"<b>Менеджер:</b> {deal.manager.full_name if deal.manager else '—'}\n"
        f"<b>Дата создания:</b> {deal.date_created.strftime('%Y-%m-%d %H:%M') if deal.date_created else '—'}\n"
        f"<b>Этап:</b> {stage_display}\n"
        f"<b>Количество задач:</b> {num_tasks}\n"
        f"<b>Прогресс:</b> {progress_percent}%"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Прогресс", callback_data=f"deal_progress_{deal.id_deal}"),
    InlineKeyboardButton("Задачи", callback_data=f"deal_tasks_{deal.id_deal}")
    )

    if user.role.value in ["admin", "manager"]:
        kb.add(
            InlineKeyboardButton("История", callback_data=f"deal_history_{deal.id_deal}"),
            InlineKeyboardButton("Изменить статус", callback_data=f"deal_edit_status_{deal.id_deal}")
        )

    kb.add(InlineKeyboardButton("Назад", callback_data="deal_view"))

    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except:
        await callback.message.answer(text, reply_markup=kb)


# ------------------------------
# Пагинация
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_view_page|"))
async def paginate_deals(callback: types.CallbackQuery):
    await safe_answer(callback)
    try:
        _, page_str, search_name, filter_by = callback.data.split("|", 3)
        page = int(page_str)
    except:
        await callback.answer("Ошибка страницы.")
        return
    await show_deals(callback, page=page, search_name=search_name, filter_by=filter_by)


# ------------------------------
# Переход к задачам сделки
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_tasks_"))
async def deal_tasks_handler(callback: types.CallbackQuery, state=None):
    await safe_answer(callback)
    deal_id = int(callback.data.split("_")[-1])
    telegram_id = str(callback.from_user.id)

    async with async_session_maker() as session:
        user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_q.scalar_one_or_none()

    if not user:
        await callback.message.answer("⚠️ Пользователь не найден.")
        return

    await show_tasks(callback, deal_id, user, page=1)
