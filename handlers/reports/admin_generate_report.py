import os
from aiogram import types, Dispatcher
from docx import Document
from docx.shared import Inches
from datetime import date, timedelta
from docx2pdf import convert  # pip install docx2pdf

async def generate_report_cb_handler(query: types.CallbackQuery):
    # Отвечаем на клик
    await query.answer("⏳ Формирую отчет...")

    # --- Выбор периода ---
    # Сразу создаем inline-кнопки для выбора периода
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("За неделю", callback_data="report_period_week"),
        InlineKeyboardButton("За месяц", callback_data="report_period_month"),
        InlineKeyboardButton("За год", callback_data="report_period_year")
    )
    await query.message.answer("Выберите период отчета:", reply_markup=kb)

# --- Обработчик выбора периода ---
async def report_period_cb_handler(query: types.CallbackQuery):
    period_map = {
        "report_period_week": 7,
        "report_period_month": 30,
        "report_period_year": 365
    }

    period = period_map.get(query.data, 30)  # по умолчанию месяц
    await query.answer(f"Генерируем отчет за последние {period} дней...")

    # --- Пути ---
    template_path = "reports/admin_report_template.docx"
    output_word = f"reports/generated/admin_report_{period}d.docx"
    output_pdf = f"reports/generated/admin_report_{period}d.pdf"

    # Заглушки диаграмм
    diagrams = {
        "{{diagram_admin_performance}}": "reports/images/admin_performance_report.png",
        "{{diagram_admin_deals}}": "reports/images/admin_deals_progress.png",
        "{{diagram_admin_sales}}": "reports/images/admin_sales_by_clients.png",
        "{{diagram_admin_funnel}}": "reports/images/admin_sales_funnel.png",
        "{{diagram_admin_timeline}}": "reports/images/admin_tasks_timeline.png",
    }

    # --- Загрузка шаблона и вставка диаграмм ---
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for placeholder, image_path in diagrams.items():
            if placeholder in paragraph.text:
                paragraph.text = ""
                run = paragraph.add_run()
                run.add_picture(image_path, width=Inches(6))

    # --- Сохраняем Word ---
    os.makedirs("reports/generated", exist_ok=True)
    doc.save(output_word)

    # --- Конвертируем в PDF ---
    convert(output_word, output_pdf)

    await query.message.answer_document(types.InputFile(output_pdf), caption=f"📄 Отчет за последние {period} дней готов!")

# --- Регистрация хендлеров ---
def register_admin_generate_report(dp: Dispatcher):
    dp.register_callback_query_handler(generate_report_cb_handler, lambda c: c.data == "report")
    dp.register_callback_query_handler(report_period_cb_handler, lambda c: c.data.startswith("report_period_"))
