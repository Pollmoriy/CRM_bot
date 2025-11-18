from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loader import dp, safe_answer
from database.db import async_session
from database.models import Deal
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5

class DeleteDealStates(StatesGroup):
    waiting_for_deal_selection = State()
    waiting_for_confirmation = State()


async def show_delete_deals_page(callback: types.CallbackQuery, page: int = 1, search_name: str = ""):
    offset_val = (page - 1) * PAGE_SIZE
    async with async_session() as session:
        query = select(Deal)
        if search_name:
            query = query.where(Deal.deal_name.ilike(f"%{search_name}%"))
        result = await session.execute(query.offset(offset_val).limit(PAGE_SIZE))
        deals = result.scalars().all()

    if not deals:
        await callback.message.answer("Список сделок пуст.")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for deal in deals:
        kb.add(
            InlineKeyboardButton(
                text=f"{deal.deal_name} ❌",
                callback_data=f"deletedeal_{deal.id_deal}"
            )
        )

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"deletedeal_page_{page-1}"))
    if len(deals) == PAGE_SIZE:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"deletedeal_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)

    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_back"))

    await callback.message.edit_text("Выберите сделку для удаления:", reply_markup=kb)
    await DeleteDealStates.waiting_for_deal_selection.set()
    await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("deletedeal_page_"), state=DeleteDealStates.waiting_for_deal_selection)
async def deletedeal_page_callback(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_delete_deals_page(callback, page)


@dp.callback_query_handler(lambda c: c.data.startswith("deletedeal_") and not c.data.startswith("deletedeal_page_"), state=DeleteDealStates.waiting_for_deal_selection)
async def confirm_delete_deal(callback: types.CallbackQuery, state: FSMContext):
    deal_id = int(callback.data.split("_")[1])
    await state.update_data(deal_id=deal_id)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Удалить", callback_data="delete_confirm_yes"),
        InlineKeyboardButton("❌ Отмена", callback_data="delete_confirm_no")
    )
    await callback.message.edit_text("Вы уверены, что хотите удалить эту сделку?", reply_markup=kb)
    await DeleteDealStates.waiting_for_confirmation.set()


@dp.callback_query_handler(lambda c: c.data.startswith("delete_confirm_"), state=DeleteDealStates.waiting_for_confirmation)
async def delete_deal_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    deal_id = data.get("deal_id")

    if callback.data == "delete_confirm_yes":
        async with async_session() as session:
            deal = (await session.execute(select(Deal).where(Deal.id_deal == deal_id))).scalar_one_or_none()
            if deal:
                await session.delete(deal)
                await session.commit()
                await callback.answer(f"Сделка '{deal.deal_name}' успешно удалена.", show_alert=True)
    else:
        await callback.answer("Удаление отменено.", show_alert=True)

    await state.finish()
    await show_delete_deals_page(callback, page=1)
