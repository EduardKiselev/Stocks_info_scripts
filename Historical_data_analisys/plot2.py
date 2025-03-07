import matplotlib.pyplot as plt
import pandas as pd

# Загрузка данных
df = pd.read_csv("temp.csv")

# Добавляем сумму extra-метрик
df['extra_sum'] = df['extra-FRED_NFCI'] + df['extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000'] + df['extra-MULTPL_SP500_PE_RATIO_MONTH']+df['cloud_flag']
df['cross_sum'] = df['cross-FRED_NFCI'] + df['cross-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000'] + df['cross-MULTPL_SP500_PE_RATIO_MONTH']+df['cloud_flag']



# Основной график
fig, ax1 = plt.subplots(figsize=(12, 6))
plt.title("Динамика показателей")

# Основная ось (левая) - FRED_NFCI и SP_SPX
ax1.set_xlabel("Время")
ax1.set_ylabel("Значения FRED_NFCI и SP_SPX", color='tab:blue')

# FRED_NFCI
ax1.plot(df['time'], df['FRED_NFCI close'], label='FRED_NFCI close', color='tab:blue')
ax1.plot(df['time'], df['FRED_NFCI Short Period Moving Average'], 
        label='FRED_NFCI Short MA', linestyle='--', color='tab:blue')

# Добавляем диапазоны для FRED_NFCI
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

# Добавляем диапазоны для SP_SPX
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

# Третья ось (правая смещённая) - MULTPL
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel("MULTPL", color='tab:purple')
ax3.plot(df['time'], df['MULTPL_SP500_PE_RATIO_MONTH close'], 
        label='MULTPL close', color='tab:purple')
ax3.plot(df['time'], df['MULTPL_SP500_PE_RATIO_MONTH Short Period Moving Average'], 
        label='MULTPL Short MA', linestyle='--', color='tab:purple')

# Добавляем диапазоны для MULTPL
if 'extra-MULTPL_SP500_PE_RATIO_MONTH_LOW' in df.columns and 'extra-MULTPL_SP500_PE_RATIO_MONTH_HIGH' in df.columns:
    ax3.fill_between(df['time'], 
                    df['extra-MULTPL_SP500_PE_RATIO_MONTH_LOW'], 
                    df['extra-MULTPL_SP500_PE_RATIO_MONTH_HIGH'], 
                    color='tab:purple', alpha=0.1,
                    label='MULTPL Range')

ax3.tick_params(axis='y', labelcolor='tab:purple')

# Легенда для основного графика
lines = ax1.get_lines() + ax2.get_lines() + ax3.get_lines()
labels = [l.get_label() for l in lines]
plt.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.savefig("plot_with_extras.png")
plt.close()

print('1 ready')


# График для extra-метрик
fig, ax = plt.subplots(figsize=(12, 6))
plt.title("Дополнительные метрики (extra-...) с суммой и SPX")

# Основная ось (левая) - extra-FRED_NFCI
# ax.set_xlabel("Время")
# ax.set_ylabel("extra-FRED_NFCI", color='tab:blue')
# ax.plot(df['time'], df['extra-FRED_NFCI'], 
#         marker='o', linestyle='--', 
#         color='tab:blue', label='FRED_NFCI')

# Вторая ось (правая) - extra-SP_SPX
# ax2 = ax.twinx()
# ax2.set_ylabel("extra-SP_SPX", color='tab:green')
# ax2.plot(df['time'], 
#         df['extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000'], 
#         marker='s', linestyle=':', 
#         color='tab:green', label='SP_SPX')

# Третья ось (правая смещённая) - extra-MULTPL
ax3 = ax.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel("extra-MULTPL", color='tab:red')
ax3.plot(df['time'], df['extra-MULTPL_SP500_PE_RATIO_MONTH'], 
        marker='^', linestyle='-.', 
        color='tab:red', label='MULTPL')

# Четвертая ось (правая смещённая дальше) - SPX
ax4 = ax.twinx()
ax4.spines['right'].set_position(('outward', 120))
ax4.set_ylabel("SPX close", color='tab:orange')
ax4.plot(df['time'], df['SPX close'], 
        linestyle='--', color='tab:orange', 
        label='SPX')

# Пятая ось (левая) - сумма extra-метрик
ax5 = ax
ax5.set_zorder(ax5.get_zorder()+1)  # Чтобы линия была поверх других
ax5.patch.set_visible(False)  # Убираем фон
ax5.plot(df['time'], df['extra_sum'], 
        color='tab:cyan', linewidth=2, 
        label='Сумма extra-метрик')

# Легенда
lines = ax.get_lines() + ax2.get_lines() + ax3.get_lines() + ax4.get_lines() + ax5.get_lines()
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.savefig("extra_metrics_plot.png")



print('2 ready')

################################################################################

# График для extra-метрик
fig, ax = plt.subplots(figsize=(12, 6))
plt.title("Дополнительные метрики (cross-...) с суммой и SPX")

# Основная ось (левая) - extra-FRED_NFCI
# ax.set_xlabel("Время")
# ax.set_ylabel("extra-FRED_NFCI", color='tab:blue')
# ax.plot(df['time'], df['extra-FRED_NFCI'], 
#         marker='o', linestyle='--', 
#         color='tab:blue', label='FRED_NFCI')

# Вторая ось (правая) - extra-SP_SPX
# ax2 = ax.twinx()
# ax2.set_ylabel("extra-SP_SPX", color='tab:green')
# ax2.plot(df['time'], 
#         df['extra-SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000'], 
#         marker='s', linestyle=':', 
#         color='tab:green', label='SP_SPX')

# Третья ось (правая смещённая) - extra-MULTPL
ax3 = ax.twinx()
ax3.spines['right'].set_position(('outward', 60))
ax3.set_ylabel("extra-MULTPL", color='tab:red')
ax3.plot(df['time'], df['cross-MULTPL_SP500_PE_RATIO_MONTH'], 
        marker='^', linestyle='-.', 
        color='tab:red', label='MULTPL')

# Четвертая ось (правая смещённая дальше) - SPX
ax4 = ax.twinx()
ax4.spines['right'].set_position(('outward', 120))
ax4.set_ylabel("SPX close", color='tab:orange')
ax4.plot(df['time'], df['SPX close'], 
        linestyle='--', color='tab:orange', 
        label='SPX')

# Пятая ось (левая) - сумма extra-метрик
ax5 = ax
ax5.set_zorder(ax5.get_zorder()+1)  # Чтобы линия была поверх других
ax5.patch.set_visible(False)  # Убираем фон
ax5.plot(df['time'], df['cross_sum'], 
        color='tab:cyan', linewidth=2, 
        label='Сумма cross-метрик')

# Легенда
lines = ax.get_lines() + ax2.get_lines() + ax3.get_lines() + ax4.get_lines() + ax5.get_lines()
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.15, 1))

plt.tight_layout()
plt.savefig("cross_metrics_plot.png")
print("Графики сохранены как plot_with_extras.png и extra_metrics_plot.png")

