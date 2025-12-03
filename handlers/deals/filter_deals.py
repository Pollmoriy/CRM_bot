from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, safe_answer
from sqlalchemy import select
from database.db import async_session_maker
from database.models import User, DealStage
from handlers.deals.view_deals import show_deals

MANAGERS_PER_PAGE = 5

# ------------------------------
# Загрузка менеджеров
# ------------------------------
async def load_managers():
    async with async_session_maker() as session:
        result = await session.execute(select(User.id_user, User.full_name).where(User.role == "manager"))
        return result.all()

# ------------------------------
# Верхняя клавиатура фильтров
# ------------------------------
def filter_menu_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📌 По стадии", callback_data="deal_filter_type|stage"),
        InlineKeyboardButton("📅 По дате", callback_data="deal_filter_type|date"),
        InlineKeyboardButton("👤 По менеджеру", callback_data="deal_filter_type|manager"),
        InlineKeyboardButton("❌ Без фильтров", callback_data="deal_filter_apply|none|none"),
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="deal_view"))
    return kb

# ------------------------------
# Клавиатура конкретных значений фильтра
# ------------------------------
async def filter_values_kb(filter_type: str, page: int = 1):
    kb = InlineKeyboardMarkup(row_width=2)
    if filter_type == "stage":
        for stage in DealStage:
            kb.add(InlineKeyboardButton(stage.value, callback_data=f"deal_filter_apply|stage|{stage.name}"))
    elif filter_type == "date":
        kb.add(
            InlineKeyboardButton("Сегодня", callback_data="deal_filter_apply|date|today"),
            InlineKeyboardButton("Последняя неделя", callback_data="deal_filter_apply|date|week"),
            InlineKeyboardButton("Последний месяц", callback_data="deal_filter_apply|date|month"),
        )
    elif filter_type == "manager":
        managers = await load_managers()
        start = (page - 1) * MANAGERS_PER_PAGE
        end = start + MANAGERS_PER_PAGE
        for m_id, full_name in managers[start:end]:
            kb.add(InlineKeyboardButton(full_name, callback_data=f"deal_filter_apply|manager|{m_id}"))
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"deal_filter_manager_page|{page-1}"))
        if end < len(managers):
            nav.append(InlineKeyboardButton("➡️ Далее", callback_data=f"deal_filter_manager_page|{page+1}"))
        if nav:
            kb.row(*nav)
    kb.add(InlineKeyboardButton("❌ Сбросить фильтр", callback_data="deal_filter_apply|none|none"))
    return kb

# ------------------------------
# Старт фильтра
# ------------------------------
async def start_filter_deal(callback: types.CallbackQuery):
    await safe_answer(callback)
    await callback.message.edit_text(
        "📊 Выберите тип фильтра:",
        reply_markup=filter_menu_kb()
    )

# ------------------------------
# Обработка выбора типа фильтра
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_filter_type|"))
async def filter_type_handler(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, filter_type = callback.data.split("|", 1)
    kb = await filter_values_kb(filter_type)
    await callback.message.edit_text("Выберите значение:", reply_markup=kb)

# ------------------------------
# Пагинация менеджеров
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_filter_manager_page|"))
async def filter_manager_page(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, page = callback.data.split("|", 1)
    kb = await filter_values_kb("manager", int(page))
    await callback.message.edit_text("Выберите менеджера:", reply_markup=kb)

# ------------------------------
# Применение фильтра
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("deal_filter_apply|"))
async def apply_filter(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, f_type, f_val = callback.data.split("|", 2)

    if f_type == "none":
        await show_deals(callback, page=1, search_name="", filter_by="")
        return

    filter_by = f"{f_type}|{f_val}"
    await show_deals(callback, page=1, search_name="", filter_by=filter_by)

# ------------------------------
# Регистрация фильтров
# ------------------------------
def register_filter_deals(dp: Dispatcher):
    dp.register_callback_query_handler(start_filter_deal, text="deal_filter")
