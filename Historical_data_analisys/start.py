import pandas as pd
from calc import custom_round
import numpy as np


PATH_DIR = "Raw_Data/"

indeces = {
   "FRED_NFCI, 1W.csv" : ["time", "close", "Short Period Moving Average"],
   "SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv" : ["time", "close", "Short Period Moving Average"],
   "MULTPL_SP500_PE_RATIO_MONTH, 1W.csv" : ["time", "close", "Short Period Moving Average"],
   "TLT, 1W.csv" : ["time", "close"],
   "SPX, 2W.csv" : ["time", "close"]

}

column_pairs = {
    "FRED_NFCI, 1W.csv": ("cross","close", "Short Period Moving Average"),  
    "SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv": ("cross","close", "Short Period Moving Average"),
    "MULTPL_SP500_PE_RATIO_MONTH, 1W.csv" : ("cross","close", "Short Period Moving Average"),
    "FRED_NFCI, 1W.csv": ("extra","close", -0.6,-0.11),
    "SP_SPX_(TVC_US03Y+3.5-0.5_ECONOMICS_USGDPYY)_ECONOMICS_USM2_10000000000, 1M.csv": ("extra","close", 4.8,16.5),
    "MULTPL_SP500_PE_RATIO_MONTH, 1W.csv" : ("extra","close", 14,25.5),

}


final_df = pd.DataFrame(columns=["time"])

for index in indeces:
    temp_data = pd.read_csv(PATH_DIR+index, usecols=indeces[index])
    temp_data["time"] = temp_data["time"].apply(custom_round)
    for column in indeces[index]:
        if column == "time":
            continue
        temp_data = temp_data.rename(columns={
                    column: index[:-4]+" "+column})
    # заполнение дыр в данных
    min_time = temp_data["time"].min()
    max_time = temp_data["time"].max()
    full_time_range = np.arange(min_time, max_time + 0.5, 0.5)
    expanded_data = pd.DataFrame({"time": full_time_range})
    merged_temp_data = pd.merge(expanded_data, temp_data, on="time", how="left")
    columns_to_fill = [col for col in merged_temp_data.columns if col != "time"]
    merged_temp_data[columns_to_fill] = merged_temp_data[columns_to_fill].ffill()

    final_df = pd.merge(final_df, merged_temp_data, on="time", how="outer")
    final_df = final_df[final_df["time"]>1000]
    final_df.to_csv("temp.csv")
    print(final_df.head())

final_df 
