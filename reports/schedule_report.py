import pandas as pd
import re


def build_schedule_report(df: pd.DataFrame) -> list[str]:
    subject_counter: dict[str, int] = {}

    for column in df.columns:
        if any(key in column for key in ("Время", "Группа", "Пара")):
            continue

        for cell in df[column].dropna():
            if not isinstance(cell, str):
                continue

            if "Предмет:" not in cell:
                continue

            match = re.search(r"Предмет:\s*(.+)", cell)
            if not match:
                continue

            subject = match.group(1).strip()
            subject_counter[subject] = subject_counter.get(subject, 0) + 1

    if not subject_counter:
        return []

    def pare_word(num: int) -> str:
        if num % 10 == 1 and num % 100 != 11:
            return "пара"
        elif 2 <= num % 10 <= 4 and not (12 <= num % 100 <= 14):
            return "пары"
        else:
            return "пар"

    result = []

    for subject, count in subject_counter.items():
        word = pare_word(count)
        result.append(f"{subject} — <b>{count} {word}</b>\n")

    return result
