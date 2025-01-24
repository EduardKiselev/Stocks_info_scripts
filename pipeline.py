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
        # Если дата не передана, используем текущую дату
        date_arg = datetime.now().strftime("%d-%m-%y")
        print(f"Дата не передана. Используется текущая дата: {date_arg}")

    # Список скриптов для выполнения
    scripts = [
        "dataread.py",
        "read_from_tinkoff.py",
        "make_countries.py",
        "calculation.py",
        "final_table.py"
    ]

    # Запускаем каждый скрипт
    for script in scripts:
        if script == "final_table.py":
            run_script(script, date_arg)  # Передаем дату только в final_table.py
        else:
            run_script(script)

    print("Пайплайн успешно завершен.")

if __name__ == "__main__":
    main()