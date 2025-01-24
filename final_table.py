import sqlite3
import pandas as pd
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
import sys
from datetime import datetime

# Подключение к БД
conn = sqlite3.connect("stocks.db")

# Чтение данных из таблицы `daily_analysis` с JOIN таблицы `countries`
query = """
SELECT da.*, c.country
FROM daily_analysis da
LEFT JOIN countries c ON da.ticker = c.ticker
"""
data = pd.read_sql(query, conn)

# Закрываем соединение с БД
conn.close()

# Преобразуем столбец `date` в формат datetime
data["date"] = pd.to_datetime(data["date"])

# Проверяем, передан ли аргумент даты
if len(sys.argv) > 1:
    date_arg = sys.argv[1]  # Получаем дату из аргументов командной строки
    try:
        # Преобразуем строку в объект datetime
        selected_date = pd.to_datetime(date_arg, format="%d-%m-%y")
    except ValueError:
        print("Неверный формат даты. Используйте формат DD-MM-YY.")
        sys.exit(1)
else:
    selected_date=datetime.today().strftime("%Y-%m-%d")

# Фильтруем данные по выбранной дате
filtered_data = data[data["date"] == selected_date]

order=['Index', 'RU', 'US', 'EU', 'HongKong']
filtered_data["country"] = pd.Categorical(filtered_data["country"], categories=order, ordered=True)

filtered_data = filtered_data.sort_values(by="country")
# filtered_data = data[data["country"]=="RU"]
# print(filtered_data)
# Создаем таблицу с флагами
flags_table = filtered_data[["ticker",
                             "country",
                             "close",
                             "ema_7",
                             "rsi_14",
                             "rsi_flag",
                             "sma_flag",
                             "macd_flag",
                             "obv_flag",
                             "ema_flag",
                             "cloud_flag"]]

# Добавляем столбец с суммой флагов
flags_table["total_flags"] = (
    flags_table["sma_flag"] +
    flags_table["macd_flag"] +
    flags_table["obv_flag"] +
    flags_table["rsi_flag"] +
    flags_table["ema_flag"] +
    flags_table["cloud_flag"]
)

# Округляем значения в столбцах `ema_7` и `rsi_14` до 2 знаков после запятой
flags_table["ema_7"] = flags_table["ema_7"].round(2)
flags_table["rsi_14"] = flags_table["rsi_14"].round(0)

# Создаем Excel-файл
wb = Workbook()
ws = wb.active

# Записываем данные в Excel
for r in dataframe_to_rows(flags_table, index=False, header=True):
    ws.append(r)

# Определяем цвета для раскрашивания
green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")  # Зеленый
red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")  # Красный

# Раскрашиваем строки в зависимости от значения `total_flags`
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
    total_flags = row[11].value  # Столбец `total_flags`индексация с 0
    if total_flags is not None:
        if total_flags > 2:
            for cell in row:
                cell.fill = green_fill  # Зеленый для total_flags > 2
        elif total_flags < -2:
            for cell in row:
                cell.fill = red_fill  # Красный для total_flags < -2


# Группируем данные по стране и считаем сумму total_flags для каждой страны
country_flags_sum = flags_table.groupby("country")["total_flags"].sum().reset_index()
country_sum = flags_table.groupby("country")["total_flags"].count().reset_index()

# Переименуем столбцы для удобства
country_flags_sum.columns = ["country", "total_flags_sum"]
country_sum.columns = ["country", "total_flags_count"]

# Объединяем данные
summary_table = pd.merge(country_flags_sum, country_sum, on="country")

# Добавляем столбец с отношением total_flags_sum / total_flags_count
summary_table["flags_ratio"] = (summary_table["total_flags_sum"] / summary_table["total_flags_count"]).round(1)

# Создаем новый лист в Excel-файле для таблицы с суммой флагов по странам
ws_summary = wb.create_sheet(title="Country Flags Summary")

# Записываем данные в новый лист
for r in dataframe_to_rows(summary_table, index=False, header=True):
    ws_summary.append(r)


# Сохраняем файл
output_file = f"flags_table_{selected_date}_colored.xlsx"
wb.save(output_file)
print(f"Таблица сохранена в файл {output_file}")