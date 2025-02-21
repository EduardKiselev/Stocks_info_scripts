import sqlite3
import subprocess
import sys
from datetime import datetime


def run_script(script_name, date_arg=None):
    """Запускает указанный скрипт с аргументом даты (если передан)."""
    try:
        if date_arg:
            subprocess.run(["python", script_name, date_arg], check=True)
        else:
            subprocess.run(["python", script_name], check=True)
        print(f"Скрипт {script_name} успешно выполнен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении скрипта {script_name}: {e}")
        sys.exit(1)


def main():
    # Получаем дату из аргументов командной строки
    if len(sys.argv) > 1:
        date_arg = sys.argv[1]
        try:
            # Проверяем, что дата в правильном формате
            datetime.strptime(date_arg, "%d-%m-%y")
        except ValueError:
            print("Неверный формат даты. Используйте формат DD-MM-YY.")
            sys.exit(1)
    else:
        # Функция для получения последней даты в таблице
        conn = sqlite3.connect("stocks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM russia_stocks")
        result = cursor.fetchone()
        if result and result[0]:
            date_arg = datetime.fromisoformat(result[0]).strftime("%d-%m-%y")
            print(f"Дата не передана. Используется последняя дата: {date_arg}")
        else:
            print("Не могу найти последнюю дату.")
            return 

    # Список скриптов для выполнения
    scripts = [
        "read_from_yahoo.py",
        "read_from_tinkoff.py",
        "make_countries.py",
        "moex_download_indexes.py",
        "calculation.py",
        "indeces_calculation.py",
        "final_table.py"
    ]

    # Запускаем каждый скрипт
    for script in scripts:
        if script == "final_table.py":
            run_script(script, date_arg)  # Передаем дату в final_table.py
        else:
            run_script(script)

    print("Пайплайн успешно завершен.")


if __name__ == "__main__":
    main()
