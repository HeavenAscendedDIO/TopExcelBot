import pandas as pd


def build_students_report(df: pd.DataFrame) -> list[str]:
    df = df[['FIO', 'Группа', 'Homework', 'Classroom']].dropna()

    problem_students = df[
        (df['Homework'] == 1) &
        (df['Classroom'] <= 3)
    ]

    if problem_students.empty:
        return []

    result = []

    for _, row in problem_students.iterrows():
        result.append(
            f"{row['FIO']} — " f"{row['Группа']}\n"
            f"📚 Домашняя работа: {row['Homework']}\n"
            f"🏫 Классная работа: {row['Classroom']}\n"
        )

    return result
