import pandas as pd
import sqlite3
import os
import pprint

# Константа для имени CSV файла
CSV_FILE = 'IRUS_M2_indicator.csv'

# Получаем имя таблицы из имени CSV файла (без расширения)
TABLE_NAME = os.path.splitext(os.path.basename(CSV_FILE))[0]

# Подключение к SQLite базе данных (если файла нет, он будет создан)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(parent_dir, 'stocks.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Чтение CSV файла в DataFrame
df = pd.read_csv('Data/' + CSV_FILE)

# Добавление новых флагов
df['flag_above_8_61'] = (df['close'] > 8.61).astype(int)
df['flag_above_7_07'] = (df['close'] > 7.07).astype(int)
df['flag_below_5_44'] = (df['close'] < 5.44).astype(int)
df['flag_below_4_7'] = (df['close'] < 4.7).astype(int)

# Создание таблицы в базе данных
# Получаем типы данных для столбцов
column_types = []
for dtype in df.dtypes:
    if dtype == 'int64':
        column_types.append('INTEGER')
    elif dtype == 'float64':
        column_types.append('REAL')
    else:
        column_types.append('TEXT')

#print(df.columns)

# Формируем строку для создания таблицы
columns_with_types = ', '.join([f'"{col}" {ctype}' for col, ctype in zip(df.columns, column_types)])
create_table_query = f'CREATE TABLE IF NOT EXISTS "{TABLE_NAME}" ({columns_with_types});'

pprint.pp(columns_with_types)

cursor.execute(create_table_query)

# Вставка данных в таблицу
df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)

# Закрытие соединения
conn.close()

print(f"Данные успешно импортированы из {CSV_FILE} в таблицу {TABLE_NAME} в базе данных stocks.db")