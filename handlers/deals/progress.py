# handlers/deals/progress.py

import io
from aiogram import types
from loader import dp, safe_answer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.db import async_session_maker
from database.models import Deal, User, Task
from PIL import Image, ImageDraw, ImageFont

@dp.callback_query_handler(lambda c: c.data.startswith("deal_progress_"))
async def show_deal_progress(callback: types.CallbackQuery):
    try:
        await safe_answer(callback)

        deal_id = int(callback.data.split("_")[-1])
        telegram_id = str(callback.from_user.id)

        waiting_msg = await callback.message.answer("⏳ Формируем прогресс...")

        # ------------------------------
        # Загрузка данных из БД
        # ------------------------------
        async with async_session_maker() as session:
            # Пользователь
            user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = user_q.scalar_one_or_none()
            if not user:
                await waiting_msg.edit_text("⚠️ Пользователь не найден.")
                return

            # Сделка
            deal_q = await session.execute(
                select(Deal).where(Deal.id_deal == deal_id).options(selectinload(Deal.tasks), selectinload(Deal.client))
            )
            deal = deal_q.scalar_one_or_none()
            if not deal:
                await waiting_msg.edit_text("⚠️ Сделка не найдена.")
                return

        # ------------------------------
        # Подсчёт прогресса
        # ------------------------------
        num_tasks = len(deal.tasks)
        completed_tasks = len([t for t in deal.tasks if getattr(t.status, "name", None) == "done"])
        progress_percent = int(completed_tasks / num_tasks * 100) if num_tasks else 0

        # ------------------------------
        # Создание диаграммы
        # ------------------------------
        size = 400
        circle_width = 40
        img = Image.new("RGBA", (size, size), (255, 255, 255, 255))  # белый фон
        draw = ImageDraw.Draw(img)

        center = size // 2
        radius = center - circle_width

        # Круг-фон
        draw.ellipse(
            (center - radius, center - radius, center + radius, center + radius),
            outline="#E0E0E0",
            width=circle_width
        )

        # Круг прогресса
        end_angle = int(360 * progress_percent / 100)
        draw.arc(
            (center - radius, center - radius, center + radius, center + radius),
            start=-90,
            end=-90 + end_angle,
            fill="#86eae9",
            width=circle_width
        )

        # Процент текста
        percent_text = f"{progress_percent}%"
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), percent_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        draw.text(
            (center - text_width // 2, center - text_height // 2),
            percent_text,
            fill="#353c6e",
            font=font
        )

        # ------------------------------
        # Преобразуем в BytesIO
        # ------------------------------
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # ------------------------------
        # Описание прогресса
        # ------------------------------
        caption = (
            f"📊 <b>Прогресс сделки:</b> {deal.deal_name}\n"
            f"<b>Клиент:</b> {deal.client.full_name if deal.client else '—'}\n"
            f"<b>Задачи всего:</b> {num_tasks}\n"
            f"<b>Выполнено:</b> {completed_tasks}\n"
            f"<b>Прогресс:</b> {progress_percent}%\n\n"
            f"Этот круг показывает визуально, насколько близка сделка к завершению. "
            f"Даже если процент равен 0, круг серый, а прогресс будет постепенно закрашиваться по мере выполнения задач. "
            f"Цвет заполнения: <code>#86eae9</code>, цвет текста процента: <code>#353c6e</code>."
        )

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data=f"deal_detail_{deal_id}"))

        await waiting_msg.delete()
        await callback.message.answer_photo(photo=buf, caption=caption, reply_markup=kb, parse_mode="HTML")

    except Exception as e:
        print(f"❌ Ошибка в show_deal_progress: {e}")
        try:
            await callback.message.answer("⚠️ Произошла ошибка при формировании прогресса.")
        except:
            pass
