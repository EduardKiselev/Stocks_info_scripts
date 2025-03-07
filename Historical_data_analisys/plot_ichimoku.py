import matplotlib
matplotlib.use('Qt5Agg')  # Или 'Qt5Agg' в зависимости от вашей системы
import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv('temp.csv')

df['time'] = pd.to_datetime(df['time'])  # Убедитесь, что время в формате datetime

# Создаем график
fig, ax1 = plt.subplots(figsize=(12, 6))

# График SPX close (левая ось)
ax1.plot(df['time'], df['SPX close'], label='SPX close', color='blue')
ax1.set_xlabel('Дата')
ax1.set_ylabel('SPX close', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Вторая ось для cloud_flag (правая ось)
ax2 = ax1.twinx()
ax2.plot(df['time'], df['cloud_flag'], label='cloud_flag', color='red', linestyle='--')
ax2.set_ylabel('cloud_flag', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Настройки графика
plt.title('SPX close и cloud_flag')
fig.tight_layout()
plt.grid(True)
plt.show()