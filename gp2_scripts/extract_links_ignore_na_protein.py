import requests
from bs4 import BeautifulSoup
import time
import csv
import re

# Отключаем предупреждения о незащищенных запросах
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Запрашиваем URL у пользователя
url = input("Введите URL для извлечения ссылок: ")

# Запрашиваем имя файла для сохранения данных в CSV
output_file = input("Введите имя файла для сохранения данных (с расширением .csv): ")

# Базовый URL для относительных ссылок
base_url = "https://www.mdsgene.org"

try:
    # Добавляем verify=False для обхода проверки SSL сертификата
    response = requests.get(url, verify=False)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Ошибка при запросе URL: {e}")
    exit(1)

html = response.text
soup = BeautifulSoup(html, "html.parser")

# Извлекаем ссылки, содержащие '/sequence_variations'
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/sequence_variations" in href:
        # Если ссылка относительная, добавляем базовый URL
        if not href.startswith("http"):
            href = base_url + href
        links.append(href)


# Функция для извлечения данных из HTML с использованием BeautifulSoup
def extract_data_from_html(soup):
    data = {
        'url': '',  # Будет заполнено в основном цикле
        'protein': 'N/A',
        'gene': 'N/A',
        'hg19': 'N/A',
        'ref_alt': 'N/A'
    }

    # Находим все строки таблицы (div с классом "row")
    rows = soup.find_all("div", class_="row")

    for row in rows:
        # Проверяем наличие двух колонок в строке
        columns = row.find_all("div", class_=lambda c: c and "columns" in c)
        if len(columns) < 2:
            continue

        # Извлекаем текст из первой колонки (заголовок)
        header_text = columns[0].get_text(strip=True)

        # Извлекаем текст или ссылку из второй колонки (значение)
        value_column = columns[1]
        # Если есть ссылка, берем её текст
        value_link = value_column.find("a")
        if value_link:
            value_text = value_link.get_text(strip=True)
        else:
            value_text = value_column.get_text(strip=True)

        # Заполняем соответствующие поля в зависимости от заголовка
        if "Protein level identifier" in header_text:
            # Извлекаем только часть после "p."
            protein_text = value_text.strip()
            data['protein'] = protein_text

        elif "Gene name:" in header_text:
            data['gene'] = value_text.strip()

        elif "Genomic location hg(19)" in header_text:
            # Извлекаем координаты
            data['hg19'] = value_text.strip()

        elif "Reference, alternative allele:" in header_text:
            data['ref_alt'] = value_text.strip()

    return data


# Счетчики для статистики
total_processed = 0
valid_records = 0
skipped_records = 0
error_records = 0

# Открываем CSV файл для записи
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['url', 'protein', 'gene', 'hg19', 'ref_alt']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    total_links = len(links)
    print(f"Найдено {total_links} ссылок. Начинаем обработку...")

    for index, link in enumerate(links, 1):
        print(f"Обработка ссылки {index} из {total_links}: {link}")
        total_processed += 1

        try:
            # Небольшая задержка, чтобы не перегружать сервер запросами
            time.sleep(1)

            # Скачиваем информацию со ссылки
            link_response = requests.get(link, verify=False)
            link_response.raise_for_status()

            # Парсим HTML
            link_soup = BeautifulSoup(link_response.text, "html.parser")

            # Ищем модальное окно с деталями мутации
            mutation_details = link_soup.find("div", id=lambda x: x and "reveal-modal" in (x or ""))
            if not mutation_details:
                # Если модальное окно не найдено, используем весь HTML документ
                mutation_details = link_soup

            # Извлекаем данные из HTML
            data = extract_data_from_html(mutation_details)
            data['url'] = link

            # Проверяем, начинается ли protein с "p."
            if not data['protein'].startswith("p."):
                print(f"Пропуск записи, так как protein не начинается с 'p.': {data['protein']}")
                skipped_records += 1
                continue

            # Записываем данные в CSV только если protein начинается с "p."
            writer.writerow(data)
            valid_records += 1

        except requests.RequestException as e:
            print(f"Ошибка при скачивании информации: {e}")
            # Записываем пустую строку с URL и ошибкой
            writer.writerow({
                'url': link,
                'protein': 'ERROR',
                'gene': 'ERROR',
                'hg19': 'ERROR',
                'ref_alt': f'Error: {str(e)}'
            })
            error_records += 1

        # Показываем прогресс
        print(f"Обработано {index}/{total_links} ссылок")

print(f"Обработка завершена. Данные сохранены в файл '{output_file}'.")
print(f"Всего обработано ссылок: {total_processed}")
print(f"Валидных записей (protein начинается с 'p.'): {valid_records}")
print(f"Пропущено записей: {skipped_records}")
print(f"Ошибок обработки: {error_records}")