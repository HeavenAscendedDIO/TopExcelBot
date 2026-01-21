import os
import pandas as pd
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.universal_report_sender import send_report_with_preview
from reports.attendance_report import build_attendance_report
from reports.lesson_topics_report import build_lesson_topics_report
from reports.students_report import build_students_report
from reports.homework_submit_report import build_homework_submit_report
from reports.schedule_report import build_schedule_report
from reports.homework_check_report import build_homework_check_report

# Словарь для хранения путей к файлам пользователей
user_files = {}

# Папка для сохранения загруженных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Меню выбора отчёта
def get_report_keyboard():
    """
    Создает инлайн-клавиатуру с кнопками для выбора типа отчёта.
    Каждая кнопка содержит callback_data, который обрабатывается в handle_callback.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📓 Расписание групп", callback_data="schedule"),
        InlineKeyboardButton("📋 Темы уроков", callback_data="topics"),
        InlineKeyboardButton("🎓 Проблемные студенты", callback_data="students"),
        InlineKeyboardButton("🏫 Посещаемость студентов", callback_data="attendance"),
        InlineKeyboardButton("📘 Проверенные домашние задания", callback_data="homework_check"),
        InlineKeyboardButton("📚 Сданные домашние задания", callback_data="homework_submit")
    )
    return keyboard


def register(bot):
    """
    Регистрация обработчиков сообщений и callback-запросов.
    """

    @bot.message_handler(content_types=["document"])
    def handle_document(message):
        """
        Принимает документ от пользователя, проверяет формат,
        сохраняет файл на диск и предлагает меню выбора отчёта.
        """
        if not message.document.file_name.endswith((".xls", ".xlsx")):
            bot.send_message(
                message.chat.id,
                "❌ <b>Неверный формат файла!\nПожалуйста, отправь Excel-файл</b>",
                parse_mode='HTML'
            )
            return

        # Получение информации о файле и скачивание
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Формирование пути для сохранения
        file_path = os.path.join(
            UPLOAD_DIR,
            f"{message.chat.id}_{message.document.file_name}"
        )

        # Запись файла на диск
        with open(file_path, "wb") as f:
            f.write(downloaded_file)

        # Сохранение пути в глобальный словарь (связываем пользователя и файл)
        user_files[message.chat.id] = file_path

        bot.send_message(
            message.chat.id,
            "📊 <b>Файл получен!</b>\nВыбери тип отчёта:",
            reply_markup=get_report_keyboard(),
            parse_mode='HTML'
        )

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        """
        Обрабатывает нажатия на кнопки меню.
        Генерирует соответствующий отчёт и отправляет результат.
        """
        chat_id = call.message.chat.id

        # Проверка: загрузил ли пользователь файл перед нажатием кнопки
        if chat_id not in user_files:
            bot.answer_callback_query(call.id, "❌ Сначала отправь Excel-файл")
            return

        # Чтение файла в Pandas DataFrame
        try:
            df = pd.read_excel(user_files[chat_id])
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ <b>Ошибка чтения файла:</b>\n{e}",
                parse_mode='HTML'
            )
            return

        # Выбор отчёта
        try:
            # === Расписание ===
            if call.data == "schedule":
                items = build_schedule_report(df)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="📖 <b>Отчёт по расписанию</b>",
                    items=items,
                    empty_message="❌ <b>Не удалось найти дисциплины в файле</b>",
                    filename_prefix="schedule_report"
                )
            # === Темы уроков ===
            elif call.data == "topics":
                items = build_lesson_topics_report(df)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="🚨 <b>Неверный формат тем уроков</b>",
                    items=items,
                    empty_message="✅ <b>Все темы уроков соответствуют формату</b>",
                    filename_prefix="invalid_lesson_topics"
                )
            # === Проблемные студенты ===
            elif call.data == "students":
                items = build_students_report(df)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="🚨 <b>Проблемные студенты</b>",
                    items=items,
                    empty_message="✅ <b>Студентов с критическими показателями не найдено</b>",
                    filename_prefix="problem_students"
                )
            # === Посещаемость ===
            elif call.data == "attendance":
                items = build_attendance_report(df)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="🚨 <b>Посещаемость ниже 40%</b>",
                    items=items,
                    empty_message="✅ <b>Преподавателей с посещаемостью ниже 40% не найдено</b>",
                    filename_prefix="low_attendance"
                )
            # === Проверка ДЗ ===
            elif call.data == "homework_check":
                # Для этого отчета нужно читать файл с двухуровневой шапкой (header=[0, 1])
                df_homework_check = pd.read_excel(user_files[chat_id], header=[0, 1])

                items = build_homework_check_report(df_homework_check)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="🚨 <b>Проверка ДЗ меньше 70%</b>",
                    items=items,
                    empty_message="✅ <b>Все преподаватели проверяют ДЗ вовремя</b>",
                    filename_prefix="low_homework_check"
                )
            # === Сдача ДЗ ===
            elif call.data == "homework_submit":
                items = build_homework_submit_report(df)
                send_report_with_preview(
                    bot=bot,
                    chat_id=chat_id,
                    title="🚨 <b>Низкий процент сдачи домашних заданий</b>",
                    items=items,
                    empty_message="✅ <b>Студентов с низким процентом сдачи домашних заданий не найдено</b>",
                    filename_prefix="low_homework_submit"
                )
            else:
                bot.send_message(chat_id, "❌ <b>Неизвестный тип отчёта</b>", parse_mode='HTML')

        # Обработка ошибки валидации колонок (если пользователь выбрал не тот отчёт)
        except ValueError as e:
            bot.send_message(
                chat_id,
                f"❌ <b>В таблице не найдены ожидаемые колонки:</b> <code>{e}</code>\n\n"
                f"Возможно, вы выбрали не тот отчёт или загрузили неверный файл",
                parse_mode='HTML'
            )
        # Ловим остальные непредвиденные ошибки
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ <b>Произошла ошибка при формировании отчёта:</b>\n{e}",
                parse_mode='HTML'
            )

        bot.answer_callback_query(call.id)
