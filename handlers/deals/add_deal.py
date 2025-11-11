from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp
from database.db import async_session
from database.models import Client, User, Deal
from sqlalchemy import select

# Константы пагинации
CLIENTS_PER_PAGE = 5
MANAGERS_PER_PAGE = 5

class AddDealStates(StatesGroup):
    waiting_for_client = State()
    waiting_for_manager = State()
    waiting_for_deal_name = State()
    waiting_for_confirmation = State()


# ---------------- Вспомогательная функция для клавиатур ----------------
def get_paginated_keyboard(items, prefix, page, per_page):
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * per_page
    end = start + per_page
    current_items = items[start:end]

    for item in current_items:
        text = item.full_name
        if isinstance(item, Client):
            callback = f"{prefix}_{item.id_client}"
        elif isinstance(item, User):
            callback = f"{prefix}_{item.id_user}"
        else:
            continue
        kb.add(InlineKeyboardButton(text=text, callback_data=callback))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"{prefix}_page_{page-1}"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton("▶️ Далее", callback_data=f"{prefix}_page_{page+1}"))
    if nav_buttons:
        kb.row(*nav_buttons)
    return kb if current_items else None


# ---------------- 1. Выбор клиента ----------------
@dp.callback_query_handler(lambda c: c.data == "deal_add")
async def start_add_deal(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    async with async_session() as session:
        clients = (await session.execute(select(Client))).scalars().all()

    if not clients:
        await callback.message.edit_text("❌ Нет клиентов для создания сделки.")
        return

    kb = get_paginated_keyboard(clients, "choose_client", 1, CLIENTS_PER_PAGE)
    await callback.message.edit_text("Выберите клиента для сделки:", reply_markup=kb)

    await state.update_data(
        clients=[{"id": c.id_client, "name": c.full_name} for c in clients]
    )
    await AddDealStates.waiting_for_client.set()


@dp.callback_query_handler(lambda c: c.data.startswith("choose_client_page_"), state=AddDealStates.waiting_for_client)
async def paginate_clients(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    clients = [Client(id_client=i["id"], full_name=i["name"]) for i in data["clients"]]
    kb = get_paginated_keyboard(clients, "choose_client", page, CLIENTS_PER_PAGE)
    await callback.answer()
    if kb:
        await callback.message.edit_text("Выберите клиента для сделки:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("choose_client_"), state=AddDealStates.waiting_for_client)
async def process_choose_client(callback: types.CallbackQuery, state: FSMContext):
    client_id = int(callback.data.split("_")[-1])
    async with async_session() as session:
        client = await session.get(Client, client_id)
        managers = (await session.execute(select(User).where(User.role=='manager'))).scalars().all()

    if not managers:
        await callback.message.edit_text("❌ Нет менеджеров для назначения сделки.")
        await state.finish()
        return

    await state.update_data(
        client_id=client_id,
        client_name=client.full_name,
        managers=[{"id": m.id_user, "name": m.full_name} for m in managers]
    )

    kb = get_paginated_keyboard(managers, "choose_manager", 1, MANAGERS_PER_PAGE)
    await callback.answer()
    await callback.message.edit_text(
        f"Клиент выбран: <b>{client.full_name}</b>\n\nТеперь выберите менеджера:",
        reply_markup=kb
    )
    await AddDealStates.waiting_for_manager.set()


# ---------------- 2. Выбор менеджера ----------------
@dp.callback_query_handler(lambda c: c.data.startswith("choose_manager_page_"), state=AddDealStates.waiting_for_manager)
async def paginate_managers(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    managers = [User(id_user=i["id"], full_name=i["name"]) for i in data["managers"]]
    kb = get_paginated_keyboard(managers, "choose_manager", page, MANAGERS_PER_PAGE)
    await callback.answer()
    if kb:
        await callback.message.edit_text("Выберите менеджера для сделки:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("choose_manager_"), state=AddDealStates.waiting_for_manager)
async def process_choose_manager(callback: types.CallbackQuery, state: FSMContext):
    manager_id = int(callback.data.split("_")[-1])
    async with async_session() as session:
        manager = await session.get(User, manager_id)

    await state.update_data(manager_id=manager_id, manager_name=manager.full_name)
    await callback.answer()
    await callback.message.edit_text("Введите название сделки:")
    await AddDealStates.waiting_for_deal_name.set()


# ---------------- 3. Ввод названия сделки ----------------
@dp.message_handler(state=AddDealStates.waiting_for_deal_name)
async def process_deal_name(message: types.Message, state: FSMContext):
    await state.update_data(deal_name=message.text)
    data = await state.get_data()
    text = (
        f"<b>Проверьте данные сделки:</b>\n\n"
        f"👤 Клиент: {data['client_name']}\n"
        f"🧑‍💼 Менеджер: {data['manager_name']}\n"
        f"📄 Название: {data['deal_name']}\n\n"
        f"Подтверждаете создание сделки?"
    )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_deal"))
    kb.add(InlineKeyboardButton("❌ Отменить", callback_data="cancel_deal"))
    await message.answer(text, reply_markup=kb)
    await AddDealStates.waiting_for_confirmation.set()


# ---------------- 4. Подтверждение ----------------
@dp.callback_query_handler(lambda c: c.data == "confirm_deal", state=AddDealStates.waiting_for_confirmation)
async def confirm_deal(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        deal = Deal(
            deal_name=data["deal_name"],
            id_client=data["client_id"],
            id_manager=data["manager_id"]
        )
        session.add(deal)
        await session.commit()
    await callback.answer()
    await callback.message.edit_text(f"✅ Сделка '{data['deal_name']}' успешно создана!")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "cancel_deal", state=AddDealStates.waiting_for_confirmation)
async def cancel_deal(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("❌ Создание сделки отменено.")
    await state.finish()
