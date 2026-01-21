import pandas as pd
import re


def build_lesson_topics_report(df: pd.DataFrame) -> list[str]:
    # Проверка на наличия колонки в таблице
    if 'Тема урока' not in df.columns:
        raise ValueError("Тема урока")

    # Регулярное выражение для проверки формата.
    # ^ - начало строки
    # \s* - возможные пробелы
    # \d+ - номер урока (цифры)
    # re.IGNORECASE - игнорируем регистр (урок/Урок)
    pattern = re.compile(r"^Урок\s*№?\s*\d+\.\s*Тема:\s*.+", re.IGNORECASE)

    invalid_topics = []

    # Проходим по всем значениям в колонке, исключая пустые ячейки (NaN)
    for topic in df['Тема урока'].dropna():
        if not pattern.match(str(topic).strip()):
            # Если строка не соответствует паттерну — добавляем в список ошибок
            invalid_topics.append(str(topic).strip())

    return invalid_topics
