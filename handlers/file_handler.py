import os
import pandas as pd
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from reports.attendance_report import build_attendance_report

user_files = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Меню выбора отчёта
def get_report_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📘 Расписание групп", callback_data="schedule"),
        InlineKeyboardButton("📋 Темы уроков", callback_data="topics"),
        InlineKeyboardButton("🎓 Проблемные студенты", callback_data="students"),
        InlineKeyboardButton("🏫 Посещаемость студентов", callback_data="attendance"),
        InlineKeyboardButton("📓 Проверенные домашние задания", callback_data="homework_check"),
        InlineKeyboardButton("📚 Сданные домашние задания", callback_data="homework_submit")
    )
    return keyboard


def register(bot):

    # Приём Excel-файла
    @bot.message_handler(content_types=["document"])
    def handle_document(message):
        if not message.document.file_name.endswith((".xls", ".xlsx")):
            bot.send_message(message.chat.id, "❌ Пожалуйста, отправь Excel-файл")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = os.path.join(
            UPLOAD_DIR,
            f"{message.chat.id}_{message.document.file_name}"
        )

        with open(file_path, "wb") as f:
            f.write(downloaded_file)

        user_files[message.chat.id] = file_path

        bot.send_message(
            message.chat.id,
            "📊 Файл получен!\nВыбери тип отчёта:",
            reply_markup=get_report_keyboard()
        )

    # Обработка кнопок
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        chat_id = call.message.chat.id

        if chat_id not in user_files:
            bot.answer_callback_query(call.id, "❌ Сначала отправь Excel-файл")
            return

        # Чтение файла
        try:
            df = pd.read_excel(user_files[chat_id])
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка чтения файла:\n{e}")
            return

        # Выбор отчёта
        if call.data == "attendance":
            text = build_attendance_report(df)

        else:
            text = "❌ Неизвестный тип отчёта"

        bot.send_message(chat_id, text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
