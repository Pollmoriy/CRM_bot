from aiogram import types
from loader import dp, safe_answer
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import async_session_maker
from database.models import Task, User, TaskStatus

TASKS_PER_PAGE = 5


# ----------------------------------------
# Хэндлер кнопки «Мои задачи»
# ----------------------------------------
@dp.message_handler(lambda m: m.text == "✅ Мои задачи")
async def employee_tasks_start(message: types.Message):
    telegram_id = str(message.from_user.id)

    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = q.scalar_one_or_none()

        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            return

        await show_employee_tasks(message, user.id_user, page=1)


# ----------------------------------------
# Список задач сотрудника
# ----------------------------------------
async def show_employee_tasks(source, employee_id: int, page: int = 1):
    async with async_session_maker() as session:
        q = await session.execute(
            select(Task)
            .where(Task.id_employee == employee_id)
            .order_by(Task.deadline.asc())
        )
        tasks = q.scalars().all()

    if not tasks:
        try:
            await source.answer("У вас пока нет задач.")
        except:
            await source.message.edit_text("У вас пока нет задач.")
        return

    start = (page - 1) * TASKS_PER_PAGE
    end = start + TASKS_PER_PAGE
    page_tasks = tasks[start:end]

    kb = InlineKeyboardMarkup(row_width=1)

    for task in page_tasks:
        deadline_text = task.deadline.strftime('%d.%m.%Y') if task.deadline else "нет срока"
        kb.add(
            InlineKeyboardButton(
                f"📝 {task.task_name} | {deadline_text}",
                callback_data=f"task_employee_details|{task.id_task}|{page}"
            )
        )

    # пагинация
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"task_employee_page|{page - 1}"))
    if end < len(tasks):
        nav.append(InlineKeyboardButton("➡️", callback_data=f"task_employee_page|{page + 1}"))
    if nav:
        kb.row(*nav)

    text = f"🧑‍💼 Ваши задачи (страница {page}/{(len(tasks)-1)//TASKS_PER_PAGE + 1}):"

    try:
        await source.answer(text, reply_markup=kb)
    except:
        await source.message.edit_text(text, reply_markup=kb)


# ----------------------------------------
# Пагинация
# ----------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_employee_page|"))
async def employee_tasks_page(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, page = callback.data.split("|")

    telegram_id = str(callback.from_user.id)

    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = q.scalar_one_or_none()

    await show_employee_tasks(callback, user.id_user, int(page))


# ----------------------------------------
# Детали задачи
# ----------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_employee_details|"))
async def employee_task_details(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, task_id, page = callback.data.split("|")

    async with async_session_maker() as session:
        q = await session.execute(select(Task).where(Task.id_task == int(task_id)))
        task = q.scalar_one_or_none()

    if not task:
        await callback.message.edit_text("Задача не найдена.")
        return

    deadline_text = task.deadline.strftime("%d.%m.%Y") if task.deadline else "нет срока"
    status_text = task.status.value

    text = (
        f"📝 <b>{task.task_name}</b>\n"
        f"\n"
        f"📄 Описание: {task.description}\n"
        f"📅 Дедлайн: {deadline_text}\n"
        f"🔖 Статус: {status_text}\n"
    )

    kb = InlineKeyboardMarkup()

    if task.status != TaskStatus.done:
        kb.add(
            InlineKeyboardButton(
                "✔️ Отметить выполненной",
                callback_data=f"task_employee_done|{task_id}|{page}"
            )
        )

    kb.add(
        InlineKeyboardButton(
            "🔙 Назад",
            callback_data=f"task_employee_back|{page}"
        )
    )

    await callback.message.edit_text(text, reply_markup=kb)


# ----------------------------------------
# Назад к списку
# ----------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_employee_back|"))
async def employee_task_back(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, page = callback.data.split("|")

    telegram_id = str(callback.from_user.id)

    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = q.scalar_one_or_none()

    await show_employee_tasks(callback, user.id_user, int(page))


# ----------------------------------------
# Выполнить задачу
# ----------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_employee_done|"))
async def employee_task_done(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, task_id, page = callback.data.split("|")

    async with async_session_maker() as session:
        q = await session.execute(select(Task).where(Task.id_task == int(task_id)))
        task = q.scalar_one_or_none()

        if not task:
            await callback.message.edit_text("Задача не найдена.")
            return

        task.status = TaskStatus.done
        await session.commit()

    await callback.message.edit_text("✔️ Задача отмечена выполненной!")
