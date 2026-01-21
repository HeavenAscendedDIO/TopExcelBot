import pandas as pd


def build_attendance_report(df: pd.DataFrame) -> list[str]:
    required_columns = {'ФИО преподавателя', 'Средняя посещаемость'}

    # Проверяем, каких колонок не хватает в файле
    missing_columns = required_columns - set(df.columns)

    # Если есть недостающие колонки, выбрасываем ошибку с их списком
    if missing_columns:
        raise ValueError(f"{', '.join(missing_columns)}")

    df = df[['ФИО преподавателя', 'Средняя посещаемость']].dropna()

    # Приводим посещаемость к числу
    df['Средняя посещаемость'] = (
        df['Средняя посещаемость']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.replace(',', '.', regex=False)
    )

    df['Средняя посещаемость'] = pd.to_numeric(
        df['Средняя посещаемость'],
        errors='coerce'
    )

    df = df.dropna(subset=['Средняя посещаемость'])

    low_attendance = df[df['Средняя посещаемость'] < 40]

    if low_attendance.empty:
        return []

    result = []

    for _, row in low_attendance.iterrows():
        result.append(f"👨🏻‍🏫 {row['ФИО преподавателя']} — {row['Средняя посещаемость']}%")

    return result
