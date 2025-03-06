import sqlite3
import time
from datetime import datetime, timedelta
import pprint
import requests

# Список интересующих индексов
indices = [
    "IMOEX", "RGBI", "RTSI", "GOLDO", "RURPLCP", "RURPLRUBCP", 
    "RURPLRUBTR", "RURPLTR", "MREDC", "RUGBICP10Y", "RUGBICP1Y", 
    "RUGBICP3Y", "RUGBICP5Y"
]

currencies = ["CNYRUB_TOM", ] # https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/CNYRUB_TOM.json?from=2023-01-01&till=2025-02-01
futures = ["USDRUBF"]    # https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities/USDRUBF.json?from=2024-01-01&till=2024-10-01


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

def fetch_currencies_data(curr, start_date, end_date):
    url = f"https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/{curr}.json"
    params = {
        "from": start_date,
        "till": end_date,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and 'history' in data and 'data' in data['history']:
            return data['history']['data']
    return None

def fetch_futures_data(curr, start_date, end_date):
    url = f"https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities/{curr}.json"
    params = {
        "from": start_date,
        "till": end_date,
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

def insert_currencies_data(conn, curr, data):
    cursor = conn.cursor()
    for entry in data:
        date = entry[1] 
        value = entry[7]
        cursor.execute('''
            INSERT OR REPLACE INTO index_data (ticker, date, value)
            VALUES (?, ?, ?)
        ''', (curr, date, value))
    conn.commit()

def insert_futures_data(conn, fut, data):
    cursor = conn.cursor()
    for entry in data:
        date = entry[1] 
        value = entry[6]
        cursor.execute('''
            INSERT OR REPLACE INTO index_data (ticker, date, value)
            VALUES (?, ?, ?)
        ''', (fut, date, value))
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
    db_path = "stocks.db"  # Путь к вашей базе данных
    conn = sqlite3.connect(db_path)
    create_tables_if_not_exist(conn)

    default_start_date = "2023-01-01"

    for index in indices:
        print(f"INDECES Processing {index}...",end=" ")
        last_date = get_last_date_for_index(conn, index)
        if last_date:
            delete_data_for_date(conn, index, last_date)
            start_date = last_date
        else:
            start_date = default_start_date
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=50)).strftime("%Y-%m-%d")
        print("Start date:", start_date, "End date:", end_date)
        # Запрашиваем данные
        data = fetch_index_data(index, start_date, end_date)
        if data:
            name = data[0][4]
            ticker = data[0][1]
            currency = data[0][14]
            insert_name(conn, ticker, name,currency)
            insert_data(conn, index, data)
        else:
            print(f"No data found for {index}.")
        time.sleep(0.5)

    for curr in currencies:
        print(f"CURR Processing {curr}...")
        last_date = get_last_date_for_index(conn, curr)
        if last_date:
            delete_data_for_date(conn, curr, last_date)
            start_date = last_date
        else:
            start_date = default_start_date
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=50)).strftime("%Y-%m-%d")

        print("Start date:", start_date, "End date:", end_date)
        data = fetch_currencies_data(curr, start_date, end_date)
        if data:
            insert_currencies_data(conn, curr, data)
        else:
            print(f"No data for Curr found: {curr}.")
        time.sleep(0.5)

    for fut in futures:
        print(f"FUTURES Processing Futures {fut}...")
        last_date = get_last_date_for_index(conn, fut)
        if last_date:
            delete_data_for_date(conn, curr, last_date)
            start_date = last_date
        else:
            start_date = default_start_date
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=50)).strftime("%Y-%m-%d")

        print("Start date:", start_date, "End date:", end_date)
        data = fetch_futures_data(fut, start_date, end_date)
        if data:
            insert_futures_data(conn, fut, data)
        else:
            print(f"No data for fut found: {fut}.")
        time.sleep(0.5)    

    conn.close()

if __name__ == "__main__":
    main()