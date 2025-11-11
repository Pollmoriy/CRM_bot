from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp, async_session
from database.models import Deal, User, Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AddDealStates(StatesGroup):
    waiting_for_client = State()
    waiting_for_manager = State()
    waiting_for_deal_name = State()

async def start_add_deal(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Client))
        clients = result.scalars().all()

    if not clients:
        await callback.message.answer("Нет клиентов для создания сделки.")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for client in clients:
        kb.add(InlineKeyboardButton(text=client.full_name, callback_data=f"choose_client_{client.id_client}"))

    # Ответ на callback сразу, без текста
    try:
        await callback.answer()
    except:
        pass  # Игнорируем, если callback устарел

    # Редактируем сообщение только если текст или клавиатура отличаются
    if callback.message.text != "Выберите клиента для сделки:" or callback.message.reply_markup != kb:
        await callback.message.edit_text("Выберите клиента для сделки:", reply_markup=kb)

    await AddDealStates.waiting_for_client.set()


@dp.callback_query_handler(lambda c: c.data.startswith("choose_client_"), state=AddDealStates.waiting_for_client)
async def process_choose_client(callback: types.CallbackQuery, state: FSMContext):
    client_id = int(callback.data.split("_")[-1])
    await state.update_data(client_id=client_id)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.role == 'manager'))
        managers = result.scalars().all()

    kb = InlineKeyboardMarkup(row_width=1)
    for manager in managers:
        kb.add(InlineKeyboardButton(text=manager.full_name, callback_data=f"choose_manager_{manager.id_user}"))

    try:
        await callback.answer()
    except:
        pass

    if callback.message.text != "Выберите менеджера для сделки:" or callback.message.reply_markup != kb:
        await callback.message.edit_text("Выберите менеджера для сделки:", reply_markup=kb)

    await AddDealStates.waiting_for_manager.set()


@dp.callback_query_handler(lambda c: c.data.startswith("choose_manager_"), state=AddDealStates.waiting_for_manager)
async def process_choose_manager(callback: types.CallbackQuery, state: FSMContext):
    manager_id = int(callback.data.split("_")[-1])
    await state.update_data(manager_id=manager_id)

    try:
        await callback.answer()
    except:
        pass

    if callback.message.text != "Введите название сделки:":
        await callback.message.edit_text("Введите название сделки:")

    await AddDealStates.waiting_for_deal_name.set()


@dp.message_handler(state=AddDealStates.waiting_for_deal_name)
async def process_deal_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    manager_id = data.get("manager_id")
    deal_name = message.text

    async with async_session() as session:
        deal = Deal(deal_name=deal_name, id_client=client_id, id_manager=manager_id)
        session.add(deal)
        await session.commit()

    await message.answer(f"Сделка '{deal_name}' успешно создана!")
    await state.finish()
