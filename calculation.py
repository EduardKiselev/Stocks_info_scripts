import sqlite3
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Подключение к БД
conn = sqlite3.connect("stocks.db")

# Чтение данных из таблиц `stocks` и `russia_stocks`
query_stocks = "SELECT * FROM stocks"
query_russia_stocks = "SELECT * FROM russia_stocks"

data_stocks = pd.read_sql(query_stocks, conn)
data_russia_stocks = pd.read_sql(query_russia_stocks, conn)

# Закрываем соединение с БД
conn.close()

# Преобразуем столбец `date` в формат datetime
data_stocks["date"] = pd.to_datetime(data_stocks["date"])
data_russia_stocks["date"] = pd.to_datetime(data_russia_stocks["date"])

# Объединяем данные из обеих таблиц
data = pd.concat([data_stocks, data_russia_stocks], ignore_index=True)

# Создаем пустой DataFrame для результатов
results = []
print("Start Calculation")

# Для каждого тикера
for ticker in data["ticker"].unique():

    # Фильтруем данные по тикеру
    ticker_data = data[data["ticker"] == ticker].copy()

    # Рассчитываем компоненты Ишимоку на дневных данных
    ichimoku = ta.ichimoku(
        ticker_data["high"], ticker_data["low"], ticker_data["close"],
        tenkan=9, kijun=26, senkou=52, include_chikou=False
    )

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

    # Рассчитываем OBV и SMA(OBV, 21)
    ticker_data["obv"] = ta.obv(ticker_data["close"], ticker_data["volume"])
    ticker_data["obv_sma_21"] = ta.sma(ticker_data["obv"], length=21)

    # Добавляем флаг по OBV
    ticker_data["obv_flag"] = 0
    ticker_data.loc[ticker_data["obv"] > ticker_data["obv_sma_21"] * 1.03, "obv_flag"] = 1
    ticker_data.loc[ticker_data["obv"] * 1.03 < ticker_data["obv_sma_21"], "obv_flag"] = -1

    # Добавляем компоненты Ишимоку в дневные данные
    ticker_data = pd.concat([ticker_data, ichimoku[0]], axis=1)

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

    # Добавляем флаг по облаку Ишимоку
    ticker_data["cloud_flag"] = 0
    ticker_data.loc[ticker_data["close"] > ticker_data["ISA_9"], "cloud_flag"] = 1
    ticker_data.loc[ticker_data["close"] < ticker_data["ISB_26"], "cloud_flag"] = -1

    # Добавляем тикер в данные
    ticker_data["ticker"] = ticker

    # Сохраняем результаты
    results.append(ticker_data)

# Объединяем все результаты в один DataFrame
results_df = pd.concat(results)

# Сохраняем результаты в новую таблицу `daily_analysis`
conn = sqlite3.connect("stocks.db")
results_df.to_sql("daily_analysis", conn, if_exists="replace", index=False)
conn.close()

print("Анализ завершен. Результаты сохранены в таблицу `daily_analysis`.")