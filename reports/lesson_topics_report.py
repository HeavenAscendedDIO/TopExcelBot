import pandas as pd
import re

def build_lesson_topics_report(df: pd.DataFrame) -> list[str]:
    pattern = re.compile(r"^Урок\s*№?\s*\d+\.\s*Тема:\s*.+", re.IGNORECASE)

    invalid_topics = []

    for topic in df['Тема урока'].dropna():
        if not pattern.match(str(topic).strip()):
            invalid_topics.append(str(topic).strip())

    return invalid_topics
