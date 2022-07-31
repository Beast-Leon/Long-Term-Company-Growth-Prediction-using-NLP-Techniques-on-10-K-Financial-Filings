#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:21:32 2022

@author: leon
"""

# 1. we need to loop to merge all the files in stock_text_y.
# Notice we will discard those with less than two rows data file
# 2. After merging all the data, we need to add sic code for each ticker
# 3. We will convert sic code to 11 categories.

import os
import re
import pandas as pd
import numpy as np
import yfinance as yf

def merge_all_files(load_path, save_path, save_path2):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    if not os.path.exists(save_path2):
        os.makedirs(save_path2)
        
    if len(os.listdir(save_path)) != 0:
        for f in os.listdir(save_path):
            os.remove(os.path.join(save_path, f))
    
    helper_dic = {}
    final_df = pd.DataFrame()
    for f in os.listdir(load_path):
        cur_full_path = os.path.join(load_path, f)
        cur_df = pd.read_csv(cur_full_path, index_col = False)
        
        if len(cur_df) > 10:
            final_df = pd.concat([final_df, cur_df])
        
        cur_tic = f.split("_")[0]
        helper_dic[cur_tic] = len(cur_df)
    
    save_file_name = "concat_stock_text_y.csv"
    save_full_path = os.path.join(save_path, save_file_name)
    final_df.to_csv(save_full_path, index = False)
    
    save_full_path2 = os.path.join(save_path2, "ticker_len_after_discard.csv")
    len_df = pd.DataFrame.from_dict(helper_dic, orient = 'index')
    len_df.to_csv(save_full_path2, index = False)

def add_sic(final_df, sic_df):
    final_df = final_df.copy(deep = True)
    sic_ls = []
    for i in range(len(final_df)):
        cur_tic = final_df['ticker'].iloc[i]
        cur_sic = sic_df[sic_df['tic_in_10k'] == cur_tic]['sic'].iloc[0]
        sic_ls.append(cur_sic)
    final_df['sic'] = sic_ls
    final_df = final_df.dropna()
    final_df['sic'] = final_df['sic'].apply(lambda x: str(int(x)))
    return final_df

def sic_to_category(sic_code):
    category = "A"
    slice_code = int(sic_code[:2])
    if slice_code <= 9:
        category = "A"
    elif 10 <= slice_code <= 14:
        category = "B"
    elif 15 <= slice_code <= 17:
        category = "C"
    elif 20 <= slice_code <= 39:
        category = "D"
    elif 40 <= slice_code <= 49:
        category = "E"
    elif 50 <= slice_code <= 51:
        category = "F"
    elif 52 <= slice_code <= 59:
        category = "G"
    elif 60 <= slice_code <= 67:
        category = "H"
    elif 70 <= slice_code <= 89:
        category = "I"
    else:
        category = "J"
    return category
    
    
def convert_sic(final_df):
    final_df = final_df.copy(deep = True)
    final_df['sic_letter'] = final_df['sic'].apply(lambda x: sic_to_category(x))
    return final_df


def change_growth(df, load_path, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    growth_ls = []
    for i in range(len(df)):
        cur_ticker = df['ticker'].iloc[i]
        cur_year = df['time'].iloc[i]
        file_name = cur_ticker + "_text_growth.csv"
        load_full_path = os.path.join(load_path, file_name)
        cur_df = pd.read_csv(load_full_path, index_col = False)
        
        cur_growth = cur_df[cur_df['time'] == cur_year]['growth'].iloc[0]
        growth_ls.append(cur_growth)
        
    df['growth'] = growth_ls
    save_full_path = os.path.join(save_path, "final_v2_dataset.csv")
    df.to_csv(save_full_path, index = False)
        
if __name__ == "__main__":
    """
    temp1 = pd.read_csv("../stock_text_y/evk_text_y.csv")
    temp2 = pd.read_csv("../stock_text_y/evok_text_y.csv")
    
    temp3 = pd.concat([temp1, temp2])
    
    temp4 = pd.DataFrame()
    
    temp5 = pd.concat([temp1, temp4])

    merge_all_files("../stock_text_y", "../stock_text_y_after_discard", "../helper")
    
    stock_text_y_concat = pd.read_csv("../stock_text_y_after_discard/concat_stock_text_y.csv")
    
    # Load ticker_sic mapping
    ticker_sic_df = pd.read_csv("../helper/ticker_sic_mapping.csv", index_col = False)
    
    new_df = add_sic(stock_text_y_concat, ticker_sic_df)
    new_new_df = convert_sic(new_df)
    new_new_df.to_csv("../stock_text_y_after_discard/final_v1_df.csv")
    
    df_sample = new_new_df.iloc[0:10]
    df_sample.to_csv("../stock_text_y_after_discard/final_v1_df_sample.csv")
    """
    final_df = pd.read_csv("../final_dataset/final_v1_dataset.csv")
    growth_sample = pd.read_csv("../stock_text_growth/arav_text_growth.csv")
    change_growth(final_df, "../stock_text_growth", "../final_dataset")
    
    