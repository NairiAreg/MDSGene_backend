import os
import pandas as pd

def save_file(file):
    file_path = os.path.join('excel', file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Загружаем Excel файл в DataFrame
    df = pd.read_excel(file_path)

    # Определение категории для каждого столбца
    def categorize_column(column_data):
        if pd.api.types.is_string_dtype(column_data):
            return "Nominal"  # Номинальный, если содержит строки
        elif pd.api.types.is_numeric_dtype(column_data):
            unique_values = column_data.nunique()
            if unique_values < 10:
                return "Ordinal"  # Порядковый, если немного уникальных значений
            elif unique_values >= 10:
                return "Interval" if column_data.min() > 0 else "Ratio"  # Интервальный или рациональный
        return "Unknown"

    # Составляем список с информацией о столбцах
    columns_info = [
        {"name": col, "category": categorize_column(df[col])}
        for col in df.columns
    ]

    # Возвращаем информацию о столбцах с категориями
    return columns_info
