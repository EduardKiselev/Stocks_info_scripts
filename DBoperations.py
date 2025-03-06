import sqlite3

# Подключение к БД (если файла нет, он будет создан)
conn = sqlite3.connect("stocks.db")
cursor = conn.cursor()


cursor.execute("""
DELETE FROM index_data where value='CNYRUB_TOM';
""")

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()

print("успешно!")
