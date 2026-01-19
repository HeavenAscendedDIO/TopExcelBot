import pandas as pd


def build_homework_check_report(df: pd.DataFrame) -> list[str]:
    required_columns = [
        ('Месяц', 'Получено'),
        ('Месяц', 'Проверено'),
        ('Неделя', 'Получено'),
        ('Неделя', 'Проверено')
    ]

    # Проверяем наличие колонок
    missing_columns = [
        f"{col[0]} - {col[1]}"
        for col in required_columns
        if col not in df.columns
    ]

    # Проверяем, есть ли 'ФИО преподавателя' в верхнем уровне заголовков
    if 'ФИО преподавателя' not in df.columns.get_level_values(0):
        missing_columns.append("ФИО преподавателя")

    if missing_columns:
        raise ValueError(", ".join(missing_columns))

    result = []

    for _, row in df.iterrows():
        fio = row.get('ФИО преподавателя')
        if isinstance(fio, pd.Series):
            fio = fio.iloc[0]

        if pd.isna(fio):
            continue

        lines = []

        try:
            month_received = row[('Месяц', 'Получено')]
            month_checked = row[('Месяц', 'Проверено')]
        except KeyError:
            month_received = month_checked = None

        if pd.notna(month_received) and pd.notna(month_checked) and month_received > 0:
            month_percent = month_checked / month_received * 100
            if month_percent < 70:
                lines.append(f"За месяц: {month_percent:.1f}%")

        try:
            week_received = row[('Неделя', 'Получено')]
            week_checked = row[('Неделя', 'Проверено')]
        except KeyError:
            week_received = week_checked = None

        if pd.notna(week_received) and pd.notna(week_checked) and week_received > 0:
            week_percent = week_checked / week_received * 100
            if week_percent < 70:
                lines.append(f"За неделю: {week_percent:.1f}%")

        if lines:
            result.append(
                fio + "\n" + "\n".join(lines) + "\n"
            )

    return result
