from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loader import dp, safe_answer
from database.db import async_session
from database.models import Deal, User, Client, DealStage
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 5

class EditDealStates(StatesGroup):
    waiting_for_deal_selection = State()
    waiting_for_field_selection = State()
    waiting_for_new_value = State()


async def show_edit_deals_page(callback: types.CallbackQuery, page: int = 1, search_name: str = ""):
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
                text=f"{deal.deal_name} ✏️",
                callback_data=f"editdeal_{deal.id_deal}"
            )
        )

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"editdeal_page_{page-1}"))
    if len(deals) == PAGE_SIZE:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"editdeal_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    kb.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_back"))

    await callback.message.edit_text("Выберите сделку для редактирования:", reply_markup=kb)
    await EditDealStates.waiting_for_deal_selection.set()
    await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("editdeal_page_"), state=EditDealStates.waiting_for_deal_selection)
async def editdeal_page_callback(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    await show_edit_deals_page(callback, page)


@dp.callback_query_handler(lambda c: c.data.startswith("editdeal_") and not c.data.startswith("editdeal_page_"), state=EditDealStates.waiting_for_deal_selection)
async def editdeal_selection(callback: types.CallbackQuery, state: FSMContext):
    deal_id = int(callback.data.split("_")[1])
    await state.update_data(deal_id=deal_id)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Название", callback_data="field_deal_name"),
        InlineKeyboardButton("Менеджер", callback_data="field_manager"),
        InlineKeyboardButton("Клиент", callback_data="field_client"),
        InlineKeyboardButton("⬅️ Назад", callback_data="editdeal_page_1")
    )

    await callback.message.edit_text("Выберите поле для редактирования сделки:", reply_markup=kb)
    await EditDealStates.waiting_for_field_selection.set()
    await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("field_"), state=EditDealStates.waiting_for_field_selection)
async def select_field_to_edit(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.replace("field_", "")
    await state.update_data(field=field)

    if field == "stage":
        # сразу покажем клавиатуру с этапами
        kb = InlineKeyboardMarkup(row_width=2)
        for stage in DealStage:
            kb.add(InlineKeyboardButton(stage.value, callback_data=f"newvalue_{stage.name}"))
        kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="editdeal_page_1"))
        await callback.message.edit_text("Выберите новый этап сделки:", reply_markup=kb)
        await EditDealStates.waiting_for_new_value.set()
    else:
        await callback.message.edit_text(f"Введите новое значение для поля '{field}':")
        await EditDealStates.waiting_for_new_value.set()
    await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data.startswith("newvalue_"), state=EditDealStates.waiting_for_new_value)
async def select_stage_value(callback: types.CallbackQuery, state: FSMContext):
    value = callback.data.replace("newvalue_", "")
    data = await state.get_data()
    deal_id = data.get("deal_id")
    field = data.get("field")

    async with async_session() as session:
        deal = (await session.execute(select(Deal).where(Deal.id_deal == deal_id))).scalar_one_or_none()
        if deal:
            if field == "stage":
                setattr(deal, field, DealStage[value].value)
            await session.commit()
            await callback.answer("Значение обновлено!", show_alert=True)
    await state.finish()
    await show_edit_deals_page(callback, page=1)


@dp.message_handler(state=EditDealStates.waiting_for_new_value)
async def save_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    field = data.get("field")
    new_value = message.text

    async with async_session() as session:
        deal = (await session.execute(select(Deal).where(Deal.id_deal == deal_id))).scalar_one_or_none()
        if not deal:
            await message.answer("Сделка не найдена.")
            await state.finish()
            return

        if field in ["manager", "client"]:
            # TODO: здесь можно сделать выбор через ID или поиск, пока просто игнорируем
            pass
        else:
            setattr(deal, field, new_value)
        await session.commit()

    await message.answer(f"Поле '{field}' обновлено для сделки '{deal.deal_name}'.")
    await state.finish()
