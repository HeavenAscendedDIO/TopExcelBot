import pandas as pd


def build_homework_submit_report(df: pd.DataFrame) -> list[str]:
    df = df[['FIO', 'Группа', 'Percentage Homework']].dropna()

    low_homework_submit = df[(df['Percentage Homework'] < 70)]

    if low_homework_submit.empty:
        return []

    result = []

    for _, row in low_homework_submit.iterrows():
        result.append(
            f"{row['FIO']} — " f"{row['Группа']}\n"
            f"📚 Процент сданных домашних заданий: {row['Percentage Homework']}%\n"
        )

    return result
