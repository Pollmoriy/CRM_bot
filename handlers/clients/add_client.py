from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp, async_session
from database.models import Client, User
from sqlalchemy import text
import re
from datetime import datetime

# FSM для добавления клиента
class AddClientStates(StatesGroup):
    full_name = State()
    phone = State()
    telegram = State()
    birth_date = State()
    segment = State()
    notes = State()

# Вспомогательная функция для валидации даты
def validate_date(date_text):
    try:
        if not date_text or date_text.strip() == "-":
            return None
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return False

# Вспомогательная функция для валидации сегмента
def validate_segment(segment_text):
    return segment_text in ("new", "regular", "vip")

# Старт добавления клиента
async def start_add_client(callback: types.CallbackQuery):
    await callback.answer()  # ⚡ мгновенный ответ Telegram
    await callback.message.answer("Введите полное имя клиента:")
    await AddClientStates.full_name.set()


# Хэндлеры для каждого шага
@dp.message_handler(state=AddClientStates.full_name)
async def add_client_full_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Имя не может быть пустым. Введите снова:")
        return
    await state.update_data(full_name=name)
    await message.answer("Введите телефон клиента (можно оставить пустым, введите '-' если нет):")
    await AddClientStates.next()


@dp.message_handler(state=AddClientStates.phone)
async def add_client_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await message.answer("Введите Telegram клиента (можно оставить пустым, введите '-' если нет):")
    await AddClientStates.next()


@dp.message_handler(state=AddClientStates.telegram)
async def add_client_telegram(message: types.Message, state: FSMContext):
    tg = message.text.strip()
    await state.update_data(telegram=tg)
    await message.answer("Введите дату рождения клиента в формате ГГГГ-ММ-ДД (можно оставить пустым, введите '-' если нет):")
    await AddClientStates.next()


@dp.message_handler(state=AddClientStates.birth_date)
async def add_client_birth_date(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    birth_date = validate_date(date_text)
    if birth_date is False:
        await message.answer("Некорректный формат даты. Введите в формате ГГГГ-ММ-ДД или '-' если нет:")
        return
    await state.update_data(birth_date=birth_date)
    await message.answer("Введите сегмент клиента (new, regular, vip):")
    await AddClientStates.next()


@dp.message_handler(state=AddClientStates.segment)
async def add_client_segment(message: types.Message, state: FSMContext):
    segment = message.text.strip()
    if not validate_segment(segment):
        await message.answer("Сегмент должен быть одним из: new, regular, vip. Введите снова:")
        return
    await state.update_data(segment=segment)
    await message.answer("Введите заметки о клиенте (можно оставить пустым, введите '-' если нет):")
    await AddClientStates.next()


@dp.message_handler(state=AddClientStates.notes)
async def add_client_notes(message: types.Message, state: FSMContext):
    notes = message.text.strip()
    await state.update_data(notes=notes)

    data = await state.get_data()
    full_name = data["full_name"]
    phone = data["phone"] if data["phone"] != "-" else None
    telegram = data["telegram"] if data["telegram"] != "-" else None
    birth_date = data["birth_date"]
    segment = data["segment"]
    notes = data["notes"] if data["notes"] != "-" else None

    await message.answer("Создаю нового клиента...")

    # ⚡ мгновенный ответ Telegram перед долгой операцией
    await message.bot.send_chat_action(message.chat.id, action="typing")

    # Добавление клиента через процедуру в БД
    try:
        async with async_session() as session:
            # Для примера используем user_id = 1, позже можно получать из telegram_id
            current_user_id = 1
            proc = text(
                "CALL add_client_proc(:full_name, :phone, :telegram, :birth_date, :segment, :notes, :user_id)"
            )
            await session.execute(
                proc,
                {
                    "full_name": full_name,
                    "phone": phone,
                    "telegram": telegram,
                    "birth_date": birth_date,
                    "segment": segment,
                    "notes": notes,
                    "user_id": current_user_id,
                },
            )
            await session.commit()
        await message.answer(f"✅ Клиент {full_name} успешно добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении клиента: {e}")

    await state.finish()
