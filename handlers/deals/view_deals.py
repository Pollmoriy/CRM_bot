# handlers/deals/view_deals.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.db import async_session_maker
from database.models import Deal, User, Client, Task

DEALS_PER_PAGE = 5

# Вспомогательная клавиатура для списка сделок
def get_deals_keyboard(deals, page=1):
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

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"deal_view_page_{page-1}"))
    if end < len(deals):
        nav_buttons.append(InlineKeyboardButton("▶️ Далее", callback_data=f"deal_view_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)

    return kb

# ====================== Список сделок ======================
@dp.callback_query_handler(lambda c: c.data == "deal_view" or c.data.startswith("deal_view_page_"))
async def show_deals(callback: types.CallbackQuery):
    await callback.answer()
    page = 1
    if callback.data.startswith("deal_view_page_"):
        page = int(callback.data.split("_")[-1])

    telegram_id = str(callback.from_user.id)
    async with async_session_maker() as session:
        # Получаем пользователя
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        role = user.role.value if user and user.role else "employee"

        # Получаем сделки в зависимости от роли
        if role == "admin":
            result = await session.execute(select(Deal).options(selectinload(Deal.tasks)))
            deals = result.scalars().all()
        elif role == "manager":
            result = await session.execute(
                select(Deal).where(Deal.id_manager == user.id_user).options(selectinload(Deal.tasks))
            )
            deals = result.scalars().all()
        else:  # employee
            # показываем только сделки, где есть задачи на этого сотрудника
            result = await session.execute(
                select(Deal).join(Task).where(Task.id_employee == user.id_user).options(selectinload(Deal.tasks))
            )
            deals = result.scalars().all()

    if not deals:
        await callback.message.edit_text("Сделок пока нет.")
        return

    kb = get_deals_keyboard(deals, page)
    await callback.message.edit_text("📁 Список сделок:", reply_markup=kb)

# ====================== Детали сделки ======================
@dp.callback_query_handler(lambda c: c.data.startswith("deal_detail_"))
async def show_deal_detail(callback: types.CallbackQuery):
    await callback.answer()
    deal_id = int(callback.data.split("_")[-1])

    telegram_id = str(callback.from_user.id)
    async with async_session_maker() as session:
        deal = await session.get(Deal, deal_id, options=[selectinload(Deal.tasks)])
        client = await session.get(Client, deal.id_client)
        manager = await session.get(User, deal.id_manager)

        user = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        role = user.role.value if user and user.role else "employee"

    num_tasks = len(deal.tasks)
    completed_tasks = len([t for t in deal.tasks if t.status.name == "done"])
    progress_percent = int(completed_tasks / num_tasks * 100) if num_tasks else 0

    text = (
        f"<b>Сделка:</b> {deal.deal_name}\n"
        f"<b>Клиент:</b> {client.full_name if client else '—'}\n"
        f"<b>Менеджер:</b> {manager.full_name if manager else '—'}\n"
        f"<b>Дата создания:</b> {deal.date_created.strftime('%Y-%m-%d %H:%M') if deal.date_created else '—'}\n"
        f"<b>Этап:</b> {deal.stage.value}\n"
        f"<b>Количество задач:</b> {num_tasks}\n"
        f"<b>Прогресс:</b> {progress_percent}%"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Прогресс", callback_data=f"deal_progress_{deal.id_deal}"),
        InlineKeyboardButton("Назад", callback_data="deal_view")
    )

    if role in ["admin", "manager"]:
        kb.add(
            InlineKeyboardButton("Изменить статус", callback_data=f"deal_edit_status_{deal.id_deal}"),
            InlineKeyboardButton("История изменений", callback_data=f"deal_history_{deal.id_deal}")
        )

    await callback.message.edit_text(text, reply_markup=kb)

# ====================== Прогресс сделки ======================
@dp.callback_query_handler(lambda c: c.data.startswith("deal_progress_"))
async def show_deal_progress(callback: types.CallbackQuery):
    await callback.answer()
    deal_id = int(callback.data.split("_")[-1])
    await callback.message.answer(f"📊 Прогресс сделки {deal_id} (пока заглушка)")
