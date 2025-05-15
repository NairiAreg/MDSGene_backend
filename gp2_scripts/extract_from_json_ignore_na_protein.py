import json
import csv
import requests
import sys

# Отключаем предупреждения о незащищенных запросах
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Запрашиваем URL для получения JSON данных
json_url = input("Введите URL для получения JSON данных: ")

# Запрашиваем имя файла для сохранения данных в CSV
output_file = input("Введите имя файла для сохранения данных (с расширением .csv): ")

# Получаем JSON данные по URL
try:
    # Добавляем verify=False для обхода проверки SSL сертификата
    response = requests.get(json_url, verify=False)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print(f"Ошибка при запросе URL: {e}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Ошибка при декодировании JSON: {e}")
    sys.exit(1)

# Проверяем, является ли data списком или словарем
if isinstance(data, dict):
    # Если данные представлены как словарь, проверяем, есть ли там список под каким-то ключом
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            data = value
            print(f"Обнаружен список данных под ключом '{key}'")
            break
    else:
        # Если массив не найден, преобразуем словарь в список из одного элемента
        data = [data]
        print("Данные представлены как одиночный словарь, преобразуем в список")
elif not isinstance(data, list):
    print("Ошибка: Полученные данные не являются ни списком, ни словарем")
    sys.exit(1)

# Открываем CSV файл для записи
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    # Определяем заголовки для CSV
    fieldnames = ['pmid', 'protein', 'gene', 'hg19', 'ref_alt']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    print(f"Найдено {len(data)} записей. Начинаем обработку...")

    # Счетчики для статистики
    total_details = 0
    valid_details = 0

    for index, entry in enumerate(data, 1):
        print(f"Обработка записи {index} из {len(data)}")

        # Для каждой записи в JSON обрабатываем все мутации
        if "mutations" in entry:
            for mutation in entry["mutations"]:
                if "details" in mutation and len(mutation["details"]) > 0:
                    for detail in mutation["details"]:
                        total_details += 1

                        # Извлекаем protein идентификатор
                        protein = detail.get("proteinLevelIdentifier", detail.get("proteinIdentifier", "N/A"))

                        # Пропускаем запись, если protein не начинается с "p."
                        if not protein.startswith("p."):
                            continue

                        valid_details += 1

                        gene = detail.get("geneName", "N/A")

                        # Извлекаем hg19 из genomicLocation
                        genomic_location = detail.get("genomicLocation", "")
                        # Проверяем, что hg действительно 19
                        hg = detail.get("hg", "")
                        hg19 = genomic_location if str(hg) == "19" else "N/A"

                        # Получаем референсный и альтернативный аллели
                        ref_alt = detail.get("referenceAlternativeAllele", "N/A")

                        # Записываем данные в CSV
                        writer.writerow({
                            'pmid': entry.get("pmid", "N/A"),
                            'protein': protein,
                            'gene': gene,
                            'hg19': hg19,
                            'ref_alt': ref_alt
                        })

    print(f"Всего обработано деталей: {total_details}")
    print(f"Валидных записей (protein начинается с 'p.'): {valid_details}")
    print(f"Пропущено записей: {total_details - valid_details}")

print(f"Обработка завершена. Данные сохранены в файл '{output_file}'.")