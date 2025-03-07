import pandas as pd
from calc import custom_round
import numpy as np
import re
import math
import pandas_ta as ta


def name_from_file(file_name: str):
    return file_name.split(",")[0]


# HYPERPARAMS
MA_WINDOW_FOR_EXTRAS = 400
LOW_QUANTILE = 0.20
HIGH_QUANTILE = 0.80
ICHIMOKY_MULT = 2

PATH_DIR = "Raw_Data/"

indeces = {
    "FRED_NFCI, 1W.csv": ["time", "close", "Short Period Moving Average"],
    "SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv": [
        "time",
        "close",
        "Short Period Moving Average",
    ],
    "MULTPL_SP500_PE_RATIO_MONTH, 1W.csv": [
        "time",
        "close",
        "Short Period Moving Average",
    ],
    "TLT, 1W.csv": ["time", "close"],
    "SPX, 2W.csv": ["time", "close","low","high"],
}

column_pairs = {
    ("FRED_NFCI, 1W.csv", "cross"): (
        "close",
        "Short Period Moving Average",
        1,  # MA<close -> UPtrend - SELL
        -1  # MA>close -> downtrend -BUY
        ),
    
    ("SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv", "cross"): (
        "close",
        "Short Period Moving Average",
        -1,  # MA>close -> downtrend - SELL
        1,  # MA<close -> UPtrend - BUY
        
    ),
    
    ("MULTPL_SP500_PE_RATIO_MONTH, 1W.csv","cross"): (
        "close",
        "Short Period Moving Average",
        -1,  # MA>close -> downtrend - SELL
        1,  # MA<close -> UPtrend - BUY
    ),
    
    ("FRED_NFCI, 1W.csv","extra"): ("extra", "close", 1, -1),
    
    ("SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv","extra"): (
        "extra",
        "close",
        -1,   # over high -SELL
        1,    # over low  -BUY
    ),
    
    ("MULTPL_SP500_PE_RATIO_MONTH, 1W.csv","extra"): ("extra",
                                            "close",
                                            -1,
                                            1
                                            ),
}


final_df = pd.DataFrame(columns=["time"])

for index in indeces:
    temp_data = pd.read_csv(PATH_DIR + index, usecols=indeces[index])
    temp_data["time"] = temp_data["time"].apply(custom_round)
    for column in indeces[index]:
        if column == "time":
            continue
        temp_data = temp_data.rename(
            columns={column: name_from_file(index) + " " + column}
        )
    # заполнение дыр в данных
    min_time = temp_data["time"].min()
    max_time = temp_data["time"].max()
    full_time_range = np.arange(min_time, max_time + 0.5, 0.5)
    expanded_data = pd.DataFrame({"time": full_time_range})
    merged_temp_data = pd.merge(expanded_data, temp_data, on="time", how="left")
    columns_to_fill = [col for col in merged_temp_data.columns if col != "time"]
    merged_temp_data[columns_to_fill] = merged_temp_data[columns_to_fill].ffill()

    final_df = pd.merge(final_df, merged_temp_data, on="time", how="outer")


for column in column_pairs:
    index_name = name_from_file(column[0])
    flag_type = column[1]
    flag_name = flag_type + "-" + index_name
    print(flag_type)
    if flag_type == "extra":
        index_column = [col for col in final_df.columns if index_name in col][0]

        final_df[flag_name+"_LOW"] = final_df[index_column].rolling(
            window=MA_WINDOW_FOR_EXTRAS,
            min_periods=100
        ).quantile(LOW_QUANTILE)

        final_df[flag_name+"_HIGH"] = final_df[index_column].rolling(
            window=MA_WINDOW_FOR_EXTRAS,
            min_periods=100
        ).quantile(HIGH_QUANTILE)

        conditions = [(final_df[index_column] > final_df[flag_name+"_HIGH"]),
                      (final_df[index_column] < final_df[flag_name+"_LOW"])]

        choices = column_pairs[column][2:4]
        final_df[flag_name] = np.select(conditions, choices, default=0)

    if flag_type == "cross":
        buy_direction = column_pairs[column][3]
        index_column = [col for col in final_df.columns if index_name in col and "Moving Average" not in col][0]
        moving_average = [col for col in final_df.columns if index_name in col and "Moving Average" in col][0]

        conditions = [(final_df[index_column] > final_df[moving_average]),
                      (final_df[index_column] < final_df[moving_average])]

        choices = column_pairs[column][2:4]
        final_df[flag_name] = np.select(conditions, choices, default=0)


# Ichimoky
high_col = [col for col in final_df.columns if "SPX" in col and "high" in col][0]
close_col = [col for col in final_df.columns if "SPX close" in col][0]
low_col = [col for col in final_df.columns if "SPX" in col and "low" in col][0]

tenkan=1*ICHIMOKY_MULT
kijun=3*ICHIMOKY_MULT
senkou=5*ICHIMOKY_MULT

ichimoku = ta.ichimoku(
    final_df[high_col], final_df[low_col], final_df[close_col],
    tenkan=tenkan, kijun=kijun, senkou=senkou, include_chikou=False
)
final_df = pd.concat([final_df, ichimoku[0]], axis=1)
final_df["cloud_flag"] = 0
print(close_col)
final_df.loc[final_df[close_col] > final_df["ISA_"+str(tenkan)], "cloud_flag"] = 1
final_df.loc[final_df[close_col] < final_df["ISB_"+str(kijun)], "cloud_flag"] = -1
# help(ta.ichimoku)

final_df = final_df[final_df["time"] > 900]
final_df["time"] = final_df["time"]*10**6
final_df['time'] = pd.to_datetime(final_df['time'], unit='s').dt.normalize()
final_df["SPX close"] = final_df["SPX close"].apply(math.log10)


final_df.to_csv("temp.csv")
print(final_df)
