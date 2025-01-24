import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime,timedelta

# Подключение к БД
conn = sqlite3.connect("stocks.db")
cursor = conn.cursor()

# Чтение списка тикеров
tickers = []
with open("tickers.txt", "r") as file:
    for line in file.readlines():
        tickers.append(line.strip().split()[0])

# Текущая дата
today = datetime.today().strftime("%Y-%m-%d")
next_day=(datetime.today()+timedelta(days=1)).strftime("%Y-%m-%d")
# Для каждого тикера
for ticker in tickers:
    # Проверяем последнюю дату в БД
    cursor.execute(f"SELECT MAX(date) FROM stocks WHERE ticker = ?", (ticker,))
    last_date = cursor.fetchone()[0]

    # Если данных нет, начинаем с 2018-01-01
    if last_date is None:
        start_date = "2018-01-01"
    else:
        # Удаляем часть времени из last_date (если она есть)
        last_date = last_date.split()[0]  # Оставляем только дату (без времени)

        # Удаляем данные за последнюю дату, так как они могут быть неполными
        cursor.execute(f"DELETE FROM stocks WHERE ticker = ? AND date LIKE ?", (ticker, f"{last_date}%"))
        conn.commit()
        # print(f"Удалены данные за {last_date} для тикера {ticker}")

        # Начинаем загрузку с последней даты
        start_date = last_date

    # Проверяем, что start_date не в будущем
    if start_date >= today:
        print(f"Пропуск тикера {ticker}: start_date ({start_date}) в будущем.")
        continue

    # Загружаем данные с Yahoo Finance
    try:
        data = yf.download(ticker, start=start_date, end=next_day)
    except Exception as e:
        print(f"Ошибка при загрузке данных для тикера {ticker}: {e}")
        continue

    # Если данные есть, добавляем их в БД
    if not data.empty:
        data.reset_index(inplace=True)
        data["ticker"] = ticker
        data = data[["Date", "ticker", "Open", "High", "Low", "Close", "Volume"]]
        data.columns = ["date", "ticker", "open", "high", "low", "close", "volume"]

        # Добавляем данные в БД
        data.to_sql("stocks", conn, if_exists="append", index=False)
        print(f"Добавлены данные для тикера {ticker} с {start_date} по {today}")

# Закрываем соединение с БД
conn.close()