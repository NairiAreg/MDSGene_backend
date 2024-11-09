import json

# Путь к JSON-файлу
JSON_FILE_PATH = "categories\\symptom_order.json"


def update_symptom_order(symptoms: list) -> bool:
    try:
        # Чтение существующих данных из JSON-файла
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)

        # Создание словаря для быстрого доступа к симптомам по их уникальным ключам
        symptom_dict = {f"{item['geneName']}_{item['symptomName']}": item for item in data}

        # Обновление порядка симптомов
        for symptom in symptoms:
            # Используем атрибуты вместо индексов
            key = f"{symptom.geneName}_{symptom.symptomName}"
            if key in symptom_dict:
                symptom_dict[key]["order"] = symptom.order
                symptom_dict[key]["categoryName"] = symptom.categoryName
            else:
                # Если симптома нет, добавляем его как новый
                symptom_dict[key] = {
                    "geneName": symptom.geneName,
                    "symptomName": symptom.symptomName,
                    "categoryName": symptom.categoryName,
                    "order": symptom.order
                }

        # Запись обновленных данных обратно в JSON-файл
        with open(JSON_FILE_PATH, "w") as file:
            json.dump(list(symptom_dict.values()), file, indent=4)

        return True
    except Exception as e:
        print(f"Error updating symptoms order: {e}")
        return False
