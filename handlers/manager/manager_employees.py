# manager_employees.py
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loader import dp, safe_answer, bot
from database.db import async_session_maker
from database.models import User, UserRole
from sqlalchemy import select


EMPLOYEES_PER_PAGE = 5

# ------------------------------
# FSM для отправки сообщения сотруднику
# ------------------------------
class SendMessageToEmployee(StatesGroup):
    waiting_text = State()

# ------------------------------
# Загрузка закрепленных сотрудников менеджера
# ------------------------------
async def load_employees(manager_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.manager_id == manager_id)
        )
        return result.scalars().all()

# ------------------------------
# Клавиатура списка сотрудников
# ------------------------------
def employees_keyboard(employees, page: int):
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * EMPLOYEES_PER_PAGE
    end = start + EMPLOYEES_PER_PAGE

    for emp in employees[start:end]:
        kb.add(
            InlineKeyboardButton(
                f"{emp.full_name} ({emp.role.value})",
                callback_data=f"employee_open|{emp.id_user}|{page}"
            )
        )

    # навигация
    nav_row = []
    if start > 0:
        nav_row.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"employee_page|{page-1}")
        )
    if end < len(employees):
        nav_row.append(
            InlineKeyboardButton("➡️ Далее", callback_data=f"employee_page|{page+1}")
        )
    if nav_row:
        kb.row(*nav_row)

    return kb

# ------------------------------
# Показ списка сотрудников
# ------------------------------
async def show_employees(message_or_callback, manager_id: int, page=1):
    is_callback = isinstance(message_or_callback, types.CallbackQuery)
    message = message_or_callback.message if is_callback else message_or_callback

    employees = await load_employees(manager_id)
    if not employees:
        text = "⚠️ У вас пока нет закрепленных сотрудников."
        if is_callback:
            await safe_answer(message_or_callback)
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    kb = employees_keyboard(employees, page)
    # Добавляем кнопку "Написать через бота" при открытии конкретного сотрудника
    text = f"👥 Ваши сотрудники (страница {page})"

    try:
        if is_callback:
            await safe_answer(message_or_callback)
            await message.edit_text(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)
    except Exception:
        await message.answer(text, reply_markup=kb)

# ------------------------------
# Обработчик кнопки "Сотрудники" из меню менеджера
# ------------------------------
@dp.message_handler(lambda message: message.text == "🧑‍💼 Сотрудники")
async def handle_manager_employees(message: types.Message):
    manager_telegram_id = str(message.from_user.id)
    async with async_session_maker() as session:
        user_q = await session.execute(
            select(User).where(User.telegram_id == manager_telegram_id)
        )
        manager = user_q.scalar_one_or_none()

    if not manager or manager.role != UserRole.manager:
        await message.answer("⚠️ Доступ запрещён. Только для менеджеров.")
        return

    await show_employees(message, manager_id=manager.id_user, page=1)

# ------------------------------
# Пагинация сотрудников
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("employee_page|"))
async def employee_page(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, page_s = callback.data.split("|")
    page = int(page_s)

    manager_telegram_id = str(callback.from_user.id)
    async with async_session_maker() as session:
        user_q = await session.execute(
            select(User).where(User.telegram_id == manager_telegram_id)
        )
        manager = user_q.scalar_one_or_none()

    if not manager:
        await callback.answer("Ошибка: менеджер не найден.")
        return

    await show_employees(callback, manager_id=manager.id_user, page=page)

# ------------------------------
# Открытие конкретного сотрудника
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("employee_open|"))
async def employee_open(callback: types.CallbackQuery):
    await safe_answer(callback)
    try:
        _, emp_id, page_s = callback.data.split("|")
        emp_id = int(emp_id)
        page = int(page_s)
    except Exception:
        await callback.answer("Ошибка открытия сотрудника.")
        return

    async with async_session_maker() as session:
        employee = await session.get(User, emp_id)

    if not employee:
        await callback.answer("Сотрудник не найден.")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "💬 Написать через бота",
            callback_data=f"msg_employee|{employee.id_user}"
        )
    )
    kb.add(
        InlineKeyboardButton("⬅️ Назад к списку", callback_data=f"employee_page|{page}")
    )

    await callback.message.edit_text(
        f"👤 {employee.full_name}\n"
        f"Роль: {employee.role.value}\n"
        f"Статус: {'Активен' if employee.is_active else 'Заблокирован'}",
        reply_markup=kb
    )

# ------------------------------
# Отправка сообщения сотруднику через FSM
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("msg_employee|"))
async def msg_employee(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, emp_id = callback.data.split("|")
    state = dp.current_state(chat=callback.from_user.id, user=callback.from_user.id)
    await state.update_data(emp_id=int(emp_id))
    await callback.message.answer("Введите сообщение для сотрудника:")
    await SendMessageToEmployee.waiting_text.set()

@dp.message_handler(state=SendMessageToEmployee.waiting_text)
async def send_msg_to_employee(message: types.Message, state: FSMContext):
    data = await state.get_data()
    emp_id = data.get("emp_id")

    async with async_session_maker() as session:
        employee = await session.get(User, emp_id)

        if not employee or not employee.telegram_id:
            await message.answer("Невозможно отправить сообщение. Telegram ID не найден.")
            await state.finish()
            return

        try:
            # 1️⃣ Отправка сообщения
            await bot.send_message(chat_id=employee.telegram_id, text=message.text)
            await message.answer("✅ Сообщение отправлено сотруднику.")

            # 2️⃣ Сохранение взаимодействия в таблицу
            interaction = Interaction(
                id_user=message.from_user.id,  # кто отправил
                id_client=None,                # можно передавать id_client, если сообщение по клиенту
                interaction_type="message",
                description=message.text
            )
            session.add(interaction)
            await session.commit()
            await message.answer("💾 Взаимодействие автоматически сохранено в истории.")

        except Exception as e:
            await message.answer(f"⚠️ Ошибка при отправке сообщения: {e}")

    await state.finish()

