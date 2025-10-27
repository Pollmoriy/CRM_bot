from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.user_crud import create_user, get_user_by_telegram_id
from database.db import async_session
from pydantic import BaseModel, validator, ValidationError
from loader import dp

from database.models import UserRole, User
class UserCreateSchema(BaseModel):
    full_name: str
    phone: str | None = None
    telegram_id: str

    @validator('full_name')
    def validate_full_name(cls, v):
        import re
        if not re.match(r"^[А-Яа-яA-Za-zЁё\s'-]+$", v):
            raise ValueError("ФИО должно содержать только буквы, пробелы или дефисы")
        if len(v.strip().split()) < 2:
            raise ValueError("ФИО должно состоять минимум из 2 слов")
        return v

# FSM состояния
class Registration(StatesGroup):
    full_name = State()
    phone = State()

# Команда /start
@dp.message_handler(commands=["start"])
async def start_registration(message: types.Message):
    async with async_session() as session:
        existing_user = await get_user_by_telegram_id(session, str(message.from_user.id))
        if existing_user:
            await message.answer(f"Привет, {existing_user.full_name}! Ваша роль: {existing_user.role.value}")
            return

    await message.answer("Привет! Введите своё ФИО (Имя Фамилия):")
    await Registration.full_name.set()

# Ввод ФИО
@dp.message_handler(state=Registration.full_name)
async def enter_full_name(message: types.Message, state: FSMContext):
    try:
        # Проверка ФИО через Pydantic
        UserCreateSchema(full_name=message.text, telegram_id=str(message.from_user.id))
    except ValidationError as e:
        await message.answer(f"Ошибка: {e.errors()[0]['msg']}\nПопробуйте ещё раз.")
        return

    await state.update_data(full_name=message.text)
    await message.answer("Введите телефон (если есть) или отправьте '-' :")
    await Registration.next()

# Ввод телефона
@dp.message_handler(state=Registration.phone)
async def enter_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_name = data['full_name']
    phone = message.text if message.text != "-" else None
    telegram_id = str(message.from_user.id)

    async with async_session() as session:
        user = await create_user(session, full_name, phone, telegram_id)
        await message.answer(f"Регистрация завершена! Ваша роль: {user.role.value}")

    await state.finish()