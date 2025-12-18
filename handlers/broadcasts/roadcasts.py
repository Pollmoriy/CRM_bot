from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from datetime import date

from loader import dp, bot, safe_answer
from database.db import async_session_maker
from database.models import User, UserRole, Client, Mailing


# ======================================================
# FSM
# ======================================================

class MailingFSM(StatesGroup):
    choose_segment = State()
    choose_template = State()
    input_text = State()


# ======================================================
# 📢 КНОПКА «РАССЫЛКИ» (админ + менеджер)
# ======================================================

@dp.message_handler(lambda m: m.text == "📢 Рассылки")
async def open_mailings_menu(message: types.Message):
    telegram_id = str(message.from_user.id)

    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )

    if not user or user.role.value not in ("admin", "manager"):
        await message.answer("⚠️ Доступ запрещён.")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✉️ Создать рассылку", callback_data="mailing_create")
    )

    await message.answer("📢 Управление рассылками", reply_markup=kb)


# ======================================================
# ✉️ СОЗДАНИЕ РАССЫЛКИ
# ======================================================

@dp.callback_query_handler(lambda c: c.data == "mailing_create")
async def mailing_create(callback: types.CallbackQuery):
    await safe_answer(callback)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Все", callback_data="segment|all"),
        InlineKeyboardButton("Новые", callback_data="segment|new"),
        InlineKeyboardButton("Постоянные", callback_data="segment|regular"),
        InlineKeyboardButton("VIP", callback_data="segment|vip"),
    )

    await callback.message.edit_text(
        "🎯 Выберите сегмент клиентов:",
        reply_markup=kb
    )
    await MailingFSM.choose_segment.set()


# ======================================================
# 🎯 ВЫБОР СЕГМЕНТА
# ======================================================

@dp.callback_query_handler(lambda c: c.data.startswith("segment|"), state=MailingFSM.choose_segment)
async def choose_segment(callback: types.CallbackQuery, state: FSMContext):
    await safe_answer(callback)
    segment = callback.data.split("|")[1]
    await state.update_data(segment=segment)

    async with async_session_maker() as session:
        templates = (await session.execute(
            select(Mailing).where(Mailing.target_segment.in_([segment, "all"]))
        )).scalars().all()

    kb = InlineKeyboardMarkup(row_width=1)

    for t in templates:
        kb.add(
            InlineKeyboardButton(
                f"📄 {t.mailing_name}",
                callback_data=f"template|{t.id_mailing}"
            )
        )

    kb.add(
        InlineKeyboardButton("✏️ Написать новый текст", callback_data="template|new"),
        InlineKeyboardButton("⬅️ Назад", callback_data="mailing_create")
    )

    await callback.message.edit_text(
        "📝 Выберите шаблон или создайте новый:",
        reply_markup=kb
    )
    await MailingFSM.choose_template.set()


# ======================================================
# 📝 ВЫБОР ШАБЛОНА
# ======================================================

@dp.callback_query_handler(lambda c: c.data.startswith("template|"), state=MailingFSM.choose_template)
async def choose_template(callback: types.CallbackQuery, state: FSMContext):
    await safe_answer(callback)
    _, template_id = callback.data.split("|")

    if template_id != "new":
        async with async_session_maker() as session:
            mailing = await session.get(Mailing, int(template_id))
        await state.update_data(text=mailing.content)

    await callback.message.edit_text(
        "✍️ Введите текст рассылки:\n\n"
        "Можно использовать переменные:\n"
        "• {name} — имя клиента"
    )
    await MailingFSM.input_text.set()


# ======================================================
# 🚀 ОТПРАВКА РАССЫЛКИ
# ======================================================

@dp.message_handler(state=MailingFSM.input_text)
async def send_mailing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    segment = data["segment"]
    text = message.text

    telegram_id = str(message.from_user.id)

    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )

        query = select(Client).where(Client.telegram.isnot(None))
        if segment != "all":
            query = query.where(Client.segment == segment)

        clients = (await session.execute(query)).scalars().all()

        session.add(
            Mailing(
                mailing_name=f"manual_{date.today()}",
                content=text,
                target_segment=segment,
                created_by=user.id_user
            )
        )

        await session.commit()

    sent = 0
    for c in clients:
        try:
            await bot.send_message(
                c.telegram,
                text.replace("{name}", c.full_name)
            )
            sent += 1
        except Exception:
            pass

    await message.answer(f"✅ Рассылка отправлена ({sent} клиентов)")
    await state.finish()


# ======================================================
# 🎂 АВТОРАССЫЛКА КО ДНЮ РОЖДЕНИЯ
# ======================================================

async def birthday_broadcast_task():
    today = date.today()

    async with async_session_maker() as session:
        mailing = await session.scalar(
            select(Mailing).where(Mailing.mailing_name == "birthday")
        )

        if not mailing:
            print("🎂 Шаблон birthday не найден")
            return

        clients = (await session.execute(
            select(Client).where(
                Client.birth_date.isnot(None),
                Client.birth_date.day == today.day,
                Client.birth_date.month == today.month,
                Client.telegram.isnot(None)
            )
        )).scalars().all()

        for c in clients:
            try:
                await bot.send_message(
                    c.telegram,
                    mailing.content.replace("{name}", c.full_name)
                )
            except Exception:
                continue

    print("🎉 Авторассылка ко дню рождения выполнена")
