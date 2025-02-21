import sqlite3

# Подключение к БД (если файла нет, он будет создан)
conn = sqlite3.connect("stocks.db")
cursor = conn.cursor()


cursor.execute("""
DELETE FROM russia_stocks where ticker='T';
""")

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()

print("успешно!")
