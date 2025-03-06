import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Пример вашего датафрейма (замените на вашу переменную)
data = pd.read_csv("temp.csv")

df = pd.DataFrame(data)

# Создаем фигуру и основную ось
fig, ax1 = plt.subplots(figsize=(12, 6))
plt.title("Динамика показателей")

# Создаем фигуру и основную ось
fig, ax1 = plt.subplots(figsize=(12, 6))
plt.title("Динамика показателей")

# Основная ось (левая) - FRED_NFCI и SP_SPX
ax1.set_xlabel("Время")
ax1.set_ylabel("Значения FRED_NFCI и SP_SPX", color='tab:blue')

# FRED_NFCI
ax1.plot(df['time'], df['FRED_NFCI close'], label='FRED_NFCI close', color='tab:blue')
ax1.plot(df['time'], df['FRED_NFCI Short Period Moving Average'], 
        label='FRED_NFCI Short MA', linestyle='--', color='tab:blue')

# Добавляем extra-FRED_NFCI_LOW и extra-FRED_NFCI_HIGH
if 'extra-FRED_NFCI_LOW' in df.columns and 'extra-FRED_NFCI_HIGH' in df.columns:
    ax1.fill_between(df['time'], 
                    df['extra-FRED_NFCI_LOW'], 
                    df['extra-FRED_NFCI_HIGH'], 
                    color='tab:blue', alpha=0.1,
                    label='FRED_NFCI Range')

# SP_SPX
ax1.plot(df['time'], df['SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000 close'], 
        label='SP_SPX close', color='tab:green')
ax1.plot(df['time'], df['SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000 Short Period Moving Average'], 
        label='SP_SPX Short MA', linestyle='--', color='tab:green')

# Добавляем extra-SP_SPX_LOW и extra-SP_SPX_HIGH
sp_spx_low_col = 'extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000_LOW'
sp_spx_high_col = 'extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000_HIGH'
if sp_spx_low_col in df.columns and sp_spx_high_col in df.columns:
    ax1.fill_between(df['time'], 
                    df[sp_spx_low_col], 
                    df[sp_spx_high_col], 
                    color='tab:green', alpha=0.1,
                    label='SP_SPX Range')

ax1.tick_params(axis='y', labelcolor='tab:blue')

# Вторая ось (правая) - TLT и SPX
ax2 = ax1.twinx()
ax2.set_ylabel("TLT и SPX close", color='tab:red')
ax2.plot(df['time'], df['TLT close'], label='TLT close', color='tab:red')
ax2.plot(df['time'], df['SPX close'], label='SPX close', linestyle='--', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:red')

# Добавляем extra-TLT и extra-SPX (если есть)
# Пример для TLT (предположим, есть столбцы extra-TLT_LOW и extra-TLT_HIGH)
if 'extra-TLT_LOW' in df.columns and 'extra-TLT_HIGH' in df.columns:
    ax2.fill_between(df['time'], 
                    df['extra-TLT_LOW'], 
                    df['extra-TLT_HIGH'], 
                    color='tab:red', alpha=0.1,
                    label='TLT Range')

# Третья ось (правая) - MULTPL
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel("MULTPL", color='tab:purple')
ax3.plot(df['time'], df['MULTPL_SP500_PE_RATIO_MONTH close'], 
        label='MULTPL close', color='tab:purple')
ax3.plot(df['time'], df['MULTPL_SP500_PE_RATIO_MONTH Short Period Moving Average'], 
        label='MULTPL Short MA', linestyle='--', color='tab:purple')

# Добавляем extra-MULTPL_LOW и extra-MULTPL_HIGH
if 'extra-MULTPL_SP500_PE_RATIO_MONTH_LOW' in df.columns and 'extra-MULTPL_SP500_PE_RATIO_MONTH_HIGH' in df.columns:
    ax3.fill_between(df['time'], 
                    df['extra-MULTPL_SP500_PE_RATIO_MONTH_LOW'], 
                    df['extra-MULTPL_SP500_PE_RATIO_MONTH_HIGH'], 
                    color='tab:purple', alpha=0.1,
                    label='MULTPL Range')

ax3.tick_params(axis='y', labelcolor='tab:purple')

# Легенда
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, 
          loc='upper left', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.savefig("plot_with_extras.png")  # Сохраняем, чтобы избежать ошибки plt.show()



# Создаем новый график для "extra"-столбцов
fig, ax = plt.subplots(figsize=(12, 6))
plt.title("Дополнительные метрики (extra-...)")

# Основная ось (левая) - для FRED_NFCI
ax.set_xlabel("Время")
ax.set_ylabel("extra-FRED_NFCI", color='tab:blue')
ax.plot(df['time'], df['extra-FRED_NFCI'], 
        marker='o', linestyle='--', 
        color='tab:blue', label='FRED_NFCI')

# Вторая ось (правая) - для SP_SPX
ax2 = ax.twinx()
ax2.set_ylabel("extra-SP_SPX", color='tab:green')
ax2.plot(df['time'], 
        df['extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000'], 
        marker='s', linestyle=':', 
        color='tab:green', label='SP_SPX')

# Третья ось (справа с смещением) - для MULTPL
ax3 = ax.twinx()
ax3.spines['right'].set_position(('outward', 60))  # Сдвигаем ось вправо
ax3.set_ylabel("extra-MULTPL", color='tab:red')
ax3.plot(df['time'], df['extra-MULTPL_SP500_PE_RATIO_MONTH'], 
        marker='^', linestyle='-.', 
        color='tab:red', label='MULTPL')

# Настройка легенды
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax.legend(lines + lines2 + lines3, labels + labels2 + labels3, 
          loc='upper left', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.savefig("extra_metrics_plot.png")
print("График 'extra_metrics_plot.png' сохранен")