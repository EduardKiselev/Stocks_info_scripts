import numpy
import pandas as pd
import os
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
import sqlite3
from dotenv import load_dotenv
import pprint
# Загрузка переменных окружения
load_dotenv()
TOKEN = os.environ['TOKEN']

# Подключение к БД
conn = sqlite3.connect("stocks.db")
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS russia_stocks (
    ticker TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY (ticker, date)
)
''')
conn.commit()


# Функция для получения последней даты в таблице
def get_last_date(ticker):
    cursor.execute("SELECT MAX(date) FROM russia_stocks WHERE ticker = ?",
                   (ticker,))
    result = cursor.fetchone()
    if result and result[0]:
        return datetime.fromisoformat(result[0])
    return None


# Функция для удаления данных за последнюю дату
def delete_last_date(ticker, last_date):
    cursor.execute("DELETE FROM russia_stocks WHERE ticker = ? AND date = ?",
                   (ticker, last_date.date().isoformat()))
    conn.commit()
    print(f"Удалены данные за {last_date.date()} для тикера {ticker}")


# Функция для получения дневных данных
def get_daily_candles(figi, ticker, days=500):
    with Client(TOKEN) as client:
        # Получаем последнюю дату из БД
        last_date = get_last_date(ticker)
        if last_date:
            # Удаляем данные за последнюю дату
            delete_last_date(ticker, last_date)
            from_date = last_date + timedelta(days=1)
        else:
            # Если данных нет, начинаем с 2023-01-01
            from_date = datetime(2023, 1, 1)

        # Ограничиваем период 500 днями
        to_date = min(from_date + timedelta(days=days),
                      now().replace(tzinfo=None)+timedelta(days=1))
        # Проверяем, что to_date > from_date
        if to_date < from_date:
            print(f"Нет новых данных для тикера {ticker}.",to_date.day,from_date.day)
            return None

        # Получаем дневные свечи
        candles = client.market_data.get_candles(
            figi=figi,
            from_=from_date,
            to=to_date,
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        )

        # Преобразуем свечи в DataFrame
        data = []
        for candle in candles.candles:
            data.append({
                "ticker": ticker,
                "date": candle.time.date().isoformat(),
                "open": candle.open.units + candle.open.nano / 1e9,
                "high": candle.high.units + candle.high.nano / 1e9,
                "low": candle.low.units + candle.low.nano / 1e9,
                "close": candle.close.units + candle.close.nano / 1e9,
                "volume": candle.volume,
            })

        df = pd.DataFrame(data)
        return df


# Функция для записи данных в БД
def save_to_db(df, ticker):
    if not df.empty:
        df.to_sql("russia_stocks", conn, if_exists="append", index=False)
        print(f"Данные сохранены в БД: {len(df)} строк, тикер {ticker}")
    else:
        print("Нет новых данных для сохранения.")


# Чтение FIGI и тикеров из файла
with open('figi.txt', 'r') as file, open('cherry.txt', 'r') as cherry:
    tickers = [line.strip().split() for line in file.readlines()]
    cherries = [line.strip().split() for line in cherry.readlines()]

    cherry_list=[]
    for cherry in cherries:
        if cherry[1] == 'RU':
            name = cherry[2] + cherry[0]
            figi = cherry[3]
            cherry_list.append([name, figi])
    tickers += cherry_list
# Обработка каждого тикера
for ticker, figi in tickers:
    print(f"Обработка тикера: {ticker} (FIGI: {figi})")
    daily_data = get_daily_candles(figi, ticker, days=500)
    if daily_data is not None:
        if daily_data.empty:
            print(f"Нет новых данных для тикера {ticker}.")
        else:
            save_to_db(daily_data, ticker)
    else:
        print(f"Ошибка при получении данных для тикера {ticker}.")

# Закрытие соединения с БД
conn.close()
