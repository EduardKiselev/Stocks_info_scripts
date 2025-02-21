import sqlite3
from datetime import datetime

import pandas as pd
import pandas_ta as ta

# Подключение к БД
conn = sqlite3.connect("indices.db")

# Чтение данных из таблицы `indices`
query_indices = "SELECT date, ticker, value as close FROM index_data"

# Загружаем данные в DataFrame
data_indices = pd.read_sql(query_indices, conn)

# Закрываем соединение с БД
conn.close()

# Преобразуем столбец `date` в формат datetime
data_indices["date"] = pd.to_datetime(data_indices["date"])

# Создаем пустой DataFrame для результатов
results = []
print("Start Index Calculation")

# Для каждого тикера
for ticker in data_indices["ticker"].unique():

    # Фильтруем данные по тикеру
    ticker_data = data_indices[data_indices["ticker"] == ticker].copy()


    # Рассчитываем SMA 7 и SMA 50
    ticker_data["sma_7"] = ta.sma(ticker_data["close"], length=7)
    ticker_data["sma_50"] = ta.sma(ticker_data["close"], length=50)

    # Добавляем флаг по SMA 7/50
    ticker_data["sma_flag"] = 0
    ticker_data.loc[ticker_data["sma_7"] > ticker_data["sma_50"] * 1.02, "sma_flag"] = 1
    ticker_data.loc[ticker_data["sma_7"] < ticker_data["sma_50"] * 0.98, "sma_flag"] = -1

    # Рассчитываем MACD (12, 26, 9)
    macd = ta.macd(ticker_data["close"], fast=12, slow=26, signal=9)
    ticker_data = pd.concat([ticker_data, macd], axis=1)

    # Добавляем флаг по MACD
    ticker_data["macd_flag"] = 0
    ticker_data.loc[ticker_data["MACD_12_26_9"] > ticker_data["MACDs_12_26_9"] * 1.05, "macd_flag"] = 1
    ticker_data.loc[ticker_data["MACD_12_26_9"] * 1.05 < ticker_data["MACDs_12_26_9"], "macd_flag"] = -1



    # Пересчитываем данные в недельные для расчета RSI и EMA7
    weekly_data = ticker_data.resample("W", on="date").agg({
        "close": "last",  # Берем последнее значение за неделю
    }).reset_index()

    # Рассчитываем RSI 14 на основе недельных данных
    weekly_data["rsi_14"] = ta.rsi(weekly_data["close"], length=14)

    # Рассчитываем EMA 7 на основе недельных данных
    weekly_data["ema_7"] = ta.ema(weekly_data["close"], length=7)

    # Объединяем недельные RSI и EMA7 с дневными данными
    ticker_data = pd.merge_asof(
        ticker_data.sort_values("date"),
        weekly_data[["date", "rsi_14", "ema_7"]].sort_values("date"),
        on="date",
        direction="backward"
    )

    # Добавляем флаг по RSI
    ticker_data["rsi_flag"] = 0
    ticker_data.loc[ticker_data["rsi_14"] < 47, "rsi_flag"] = -1
    ticker_data.loc[ticker_data["rsi_14"] > 53, "rsi_flag"] = 1

    # Добавляем флаг по EMA7
    ticker_data["ema_flag"] = 0
    ticker_data.loc[ticker_data["close"] > ticker_data["ema_7"] * 1.01, "ema_flag"] = 1
    ticker_data.loc[ticker_data["close"] < ticker_data["ema_7"] * 0.99, "ema_flag"] = -1


    # Добавляем тикер в данные
    ticker_data["ticker"] = ticker

    # Сохраняем результаты
    results.append(ticker_data)

# Объединяем все результаты в один DataFrame
results_df = pd.concat(results)

# Сохраняем результаты в новую таблицу `indices_analysis`
conn = sqlite3.connect("indices.db")
results_df.to_sql("indices_analysis", conn, if_exists="replace", index=False)
conn.close()

print("Анализ завершен. Результаты сохранены в таблицу `indices_analysis`.")