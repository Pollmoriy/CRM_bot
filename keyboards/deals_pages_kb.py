from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from database.db import async_session_maker
from database.models import User, DealStage

MANAGERS_PER_PAGE = 5

# ------------------------------
# Загрузка менеджеров
# ------------------------------
async def load_managers():
    async with async_session_maker() as session:
        result = await session.execute(select(User.id_user, User.full_name).where(User.role == "manager"))
        return result.all()

# ------------------------------
# Верхняя клавиатура для сделок
# ------------------------------
def top_deals_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Поиск сделки", callback_data="deal_search"),
        InlineKeyboardButton("📊 Фильтр", callback_data="deal_filter"),
    )
    kb.add(
        InlineKeyboardButton("❌ Сбросить фильтр", callback_data="deal_filter_apply|none|none")
    )
    return kb

# ------------------------------
# Клавиатура навигации между страницами сделок
# ------------------------------
def deals_nav_kb(current_page: int, has_next: bool, search_name: str = "", filter_by: str = ""):
    kb = InlineKeyboardMarkup(row_width=2)
    nav_buttons = []

    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"deal_view_page|{current_page-1}|{search_name}|{filter_by}")
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton("➡️ Далее", callback_data=f"deal_view_page|{current_page+1}|{search_name}|{filter_by}")
        )

    if nav_buttons:
        kb.row(*nav_buttons)

    return kb
