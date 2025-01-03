import pandas as pd
import os
import json
from difflib import get_close_matches


def suggest_column_fixes(df, expected_columns):
    """
    Предлагает исправления для колонок, которые не соответствуют ожидаемым.
    :param df: DataFrame с текущими колонками.
    :param expected_columns: Список ожидаемых колонок.
    :return: Словарь с предложенными исправлениями {текущее_название: предложенное_название}.
    """
    suggestions = {}

    # Исключаем колонки, которые уже существуют в DataFrame
    existing_columns = set(df.columns)
    remaining_expected_columns = expected_columns - existing_columns

    for col in df.columns:
        if col not in expected_columns:
            # Ищем близкие совпадения среди оставшихся ожидаемых колонок
            close_matches = get_close_matches(col, remaining_expected_columns, n=1)

            # Если есть близкие совпадения, предлагаем их
            if close_matches:
                suggestions[col] = close_matches[0]
            else:
                # Если нет близких совпадений, проверяем, содержит ли название колонки ожидаемое ключевое слово
                for expected_col in remaining_expected_columns:
                    if expected_col in col:
                        suggestions[col] = expected_col
                        break  # Предлагаем первое найденное совпадение

    return suggestions, remaining_expected_columns


def load_responses(response_file):
    """
    Загружает ответы пользователя из файла, если он существует.
    :param response_file: Путь к файлу с ответами.
    :return: Словарь с ответами или пустой словарь, если файл не существует.
    """
    if os.path.exists(response_file):
        with open(response_file, "r") as file:
            return json.load(file)
    return {}


def save_responses(response_file, responses):
    """
    Сохраняет ответы пользователя в файл.
    :param response_file: Путь к файлу с ответами.
    :param responses: Словарь с ответами.
    """
    with open(response_file, "w") as file:
        json.dump(responses, file, indent=4)


def interactive_column_fix(df, suggestions, response_file):
    """
    Интерактивно предлагает пользователю исправить названия колонок.
    :param df: DataFrame с текущими колонками.
    :param suggestions: Словарь с предложенными исправлениями.
    :param response_file: Путь к файлу с ответами.
    :return: DataFrame с исправленными колонками (если пользователь подтвердил изменения).
    """
    if not suggestions:
        print("Все колонки соответствуют ожидаемым названиям.")
        return df

    # Загружаем ответы из файла, если он существует
    responses = load_responses(response_file)

    print("Обнаружены несоответствия в названиях колонок:")
    for current_col, suggested_col in suggestions.items():
        if current_col in responses:
            # Если ответ уже есть в файле, используем его
            response = responses[current_col]
        else:
            # Иначе запрашиваем ответ у пользователя
            response = input(f"Переименовать колонку '{current_col}' в '{suggested_col}'? (y/n): ").strip().lower()
            responses[current_col] = response  # Сохраняем ответ

        if response == 'y':
            df.rename(columns={current_col: suggested_col}, inplace=True)
            print(f"Колонка '{current_col}' переименована в '{suggested_col}'.")
        else:
            print(f"Колонка '{current_col}' осталась без изменений.")

    # Сохраняем ответы в файл
    save_responses(response_file, responses)

    return df


def process_disease_abbrev(df):
    """
    Обрабатывает колонку disease_abbrev: удаляет лишние пробелы и фильтрует строки по уникальным значениям.
    :param df: DataFrame с данными.
    :return: Обработанный DataFrame.
    """
    if "disease_abbrev" not in df.columns:
        print("Колонка 'disease_abbrev' отсутствует в файле.")
        return df

    # Удаляем лишние пробелы в начале и конце строк
    df["disease_abbrev"] = df["disease_abbrev"].str.strip()

    # Получаем уникальные значения
    unique_values = df["disease_abbrev"].unique()

    # Создаем маску для фильтрации строк
    mask = pd.Series(False, index=df.index)

    for value in unique_values:
        response = input(
            f"Хотите оставить строки со значением '{value}' в колонке 'disease_abbrev'? (y/n): ").strip().lower()
        if response == 'y':
            mask |= (df["disease_abbrev"] == value)

    # Фильтруем DataFrame по маске
    df = df[mask]

    return df


def fix_and_save_columns(file_path, expected_columns, column_mapping=None):
    """
    Исправляет названия колонок в файле и сохраняет изменения.
    :param file_path: Путь к файлу.
    :param expected_columns: Список ожидаемых названий колонок.
    :param column_mapping: Словарь для маппинга нестандартных названий на стандартные.
    """
    try:
        # Определяем движок для чтения файла
        _, file_extension = os.path.splitext(file_path)
        engine = "openpyxl" if file_extension.lower() == ".xlsx" else "xlrd"

        # Чтение файла
        df = pd.read_excel(file_path, engine=engine)

        # Приводим все названия колонок к нижнему регистру и удаляем лишние пробелы
        df.columns = df.columns.str.lower().str.strip()

        # Если предоставлен маппинг, применяем его
        if column_mapping:
            df.rename(columns=column_mapping, inplace=True)

        # Проверяем колонки и предлагаем исправления
        suggestions, missing_columns = suggest_column_fixes(df, expected_columns)

        # Выводим список отсутствующих колонок
        if missing_columns:
            print("\nСледующие колонки отсутствуют в файле:")
            for col in missing_columns:
                print(f"- {col}")

            # Предлагаем вставить отсутствующие колонки
            for col in missing_columns:
                response = input(
                    f"Хотите вставить колонку '{col}' и заполнить её значением -99? (y/n): ").strip().lower()
                if response == 'y':
                    df[col] = -99
                    print(f"Колонка '{col}' добавлена и заполнена значением -99.")
        else:
            print("\nВсе ожидаемые колонки присутствуют в файле.")

        # Обрабатываем колонку disease_abbrev
        df = process_disease_abbrev(df)

        # Создаем путь к файлу с ответами
        response_file = os.path.splitext(file_path)[0] + "_responses.json"

        # Исправляем колонки с учетом ответов пользователя
        df = interactive_column_fix(df, suggestions, response_file)

        # Если были внесены изменения, сохраняем обновленный файл
        if suggestions or missing_columns:
            save_response = input("Хотите сохранить изменения в файл? (y/n): ").strip().lower()
            if save_response == 'y':
                df.to_excel(file_path, index=False, engine=engine)
                print(f"Файл '{file_path}' успешно обновлен.")
            else:
                print("Изменения не сохранены.")
        else:
            print("Все колонки соответствуют ожидаемым названиям. Изменения не требуются.")

    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {str(e)}")
        raise e


if __name__ == "__main__":
    # Ожидаемые колонки (без колонок, заканчивающихся на _sympt)
    expected_columns = {
        "pmid", "author, year", "study_design", "genet_methods", "lower_age_limit",
        "upper_age_limit", "comments_study", "family_id", "individual_id",
        "disease_abbrev", "clinical_info", "ethnicity", "country", "sex",
        "index_pat", "famhx", "num_het_mut_affected", "num_hom_mut_affected",
        "num_het_mut_unaffected", "num_hom_mut_unaffected", "num_wildtype_affected",
        "num_wildtype_unaffected", "status_clinical", "aae", "aao", "duration",
        "age_dx", "age_death", "hg_version", "genome_build", "gene1",
        "physical_location1", "reference_allele1", "observed_allele1", "mut1_g",
        "mut1_c", "mut1_p", "mut1_alias_original", "mut1_alias", "mut1_genotype",
        "mut1_type", "gnomad1 v2.1.1", "gnomad1 v4.0.0", "gene2", "physical_location2",
        "reference_allele2", "observed_allele2", "mut2_g", "mut2_c", "mut2_p",
        "mut2_alias_original", "mut2_alias", "mut2_genotype", "mut2_type",
        "gnomad2 v2.1.1", "gnomad2 v4.0.0", "gene3", "physical_location3",
        "reference_allele3", "observed_allele3", "mut3_g", "mut3_c", "mut3_p",
        "mut3_alias", "mut3_genotype", "mut_3_type", "gnomad3 v2.1.1", "gnomad3 v4.0.0",
        "motor_instrument1", "motor_score1", "motor_instrument2", "motor_score2",
        "nms_scale", "levodopa_response", "response_quantification", "depression_scale",
        "anxiety_scale", "psychotic_scale", "cognitive_decline_scale", "comments_pat",
        "pathogenicity1", "pathogenicity2", "pathogenicity3", "cadd_1", "cadd_2",
        "cadd_3", "fun_evidence_pos_1", "fun_evidence_pos_2", "fun_evidence_pos_3",
        "mdsgene_decision", "entry", "comment"
    }

    # Путь к файлу (можно передать как аргумент командной строки)
    file_path = input("Введите путь к файлу Excel: ").strip()

    # Запуск функции исправления колонок
    fix_and_save_columns(file_path, expected_columns)