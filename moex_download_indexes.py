import sqlite3
import time
from datetime import datetime, timedelta

import requests

# Список интересующих индексов
indices = [
    "IMOEX", "RGBI", "RTSI", "GOLDO", "RURPLCP", "RURPLRUBCP", 
    "RURPLRUBTR", "RURPLTR", "MREDC", "RUGBICP10Y", "RUGBICP1Y", 
    "RUGBICP3Y", "RUGBICP5Y"
]

# Функция для создания таблиц, если они отсутствуют
def create_tables_if_not_exist(conn):
    cursor = conn.cursor()
    
    # Таблица для хранения данных по индексам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            date TEXT,
            value REAL,
            UNIQUE(ticker, date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE,
            name TEXT,
            currency TEXT
        )
    ''')    
    
    conn.commit()

# Функция для получения данных по индексу за определенный период
def fetch_index_data(index, start_date, end_date):
    url = f"https://iss.moex.com/iss/history/engines/stock/markets/index/securities/{index}.json"
    params = {
        "from": start_date,
        "till": end_date,
        "iss.meta": "off"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and 'history' in data and 'data' in data['history']:
            return data['history']['data']
    return None

# Функция для получения последней даты для индекса из базы данных
def get_last_date_for_index(conn, index):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(date) FROM index_data
        WHERE ticker = ?
    ''', (index,))
    result = cursor.fetchone()
    return result[0] if result[0] else None

# Функция для удаления данных за определенную дату
def delete_data_for_date(conn, index, date):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM index_data
        WHERE ticker = ? AND date = ?
    ''', (index, date))
    conn.commit()

# Функция для вставки данных в базу данных
def insert_data(conn, index, data):
    cursor = conn.cursor()
    for entry in data:
        date = entry[2]  # TRADEDATE находится на позиции 2
        value = entry[5]  # CLOSE находится на позиции 5
        cursor.execute('''
            INSERT OR REPLACE INTO index_data (ticker, date, value)
            VALUES (?, ?, ?)
        ''', (index, date, value))
    conn.commit()


def insert_name(conn, index, name, currency):
    cursor = conn.cursor()
    cursor.execute('''
            INSERT OR REPLACE INTO index_names (ticker, name, currency)
            VALUES (?, ?, ?)
        ''', (index, name,currency))
    conn.commit()


# Основная функция для обновления данных
def main():
    db_path = "indices.db"  # Путь к вашей базе данных
    conn = sqlite3.connect(db_path)

    # Создаем таблицы, если они отсутствуют
    create_tables_if_not_exist(conn)

    # Начальная дата по умолчанию
    default_start_date = "2023-01-01"

    for index in indices:
        print(f"Processing {index}...",end=" ")

        # Получаем последнюю дату для индекса из базы данных
        last_date = get_last_date_for_index(conn, index)

        # Определяем дату начала запроса
        if last_date:
            # Если данные за последнюю дату уже есть, удаляем их
            delete_data_for_date(conn, index, last_date)
            start_date = last_date
        else:
            # Если данных нет, используем начальную дату по умолчанию
            start_date = default_start_date

        # Вычисляем конечную дату (50 дней вперед)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=50)).strftime("%Y-%m-%d")
        print("Start date:", start_date, "End date:", end_date)
        # Запрашиваем данные
        data = fetch_index_data(index, start_date, end_date)
        if data:
            # print(f"Data found for {index}, inserting into database...")
            name = data[0][4]
            ticker = data[0][1]
            currency = data[0][14]
            insert_name(conn, ticker, name,currency)
            insert_data(conn, index, data)
        else:
            print(f"No data found for {index}.")

        # Задержка на 1/2 секунды после запроса
        time.sleep(0.5)

    conn.close()

if __name__ == "__main__":
    main()