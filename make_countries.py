import sqlite3


tickers = []
# Создаем словарь для хранения тикеров и стран
ticker_country = {}

with open("tickers.txt", "r") as file:
    for line in file.readlines():
        ticker = line.strip().split()[0]
        tickers.append(ticker)
        if ticker[0] == '^':
            ticker_country[ticker] = 'Index'    
        elif '.HK' in ticker:
            ticker_country[ticker] = 'HongKong'
        elif line.split()[1] == "US":
            ticker_country[ticker] = 'US'
        elif line.split()[1] == 'EU':
            ticker_country[ticker] = 'EU'
with open("figi.txt",'r') as file:
    for line in file.readlines():
        ticker = line.strip().split()[0]
        if ticker in ['IMOEX','RTSI','RGBI']:
            ticker_country[ticker]='Index'
        else:
            ticker_country[ticker]='RU'
# Подключаемся к базе данных (или создаем, если она не существует)
conn = sqlite3.connect('stocks.db')
cursor = conn.cursor()

# Создаем таблицу countries
cursor.execute('''
CREATE TABLE IF NOT EXISTS countries (
    ticker TEXT PRIMARY KEY,
    country TEXT NOT NULL
)
''')

# Вставляем данные в таблицу
for ticker, country in ticker_country.items():
    cursor.execute('''
    INSERT OR REPLACE INTO countries (ticker, country)
    VALUES (?, ?)
    ''', (ticker, country))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Таблица создана, данные добавлены.")