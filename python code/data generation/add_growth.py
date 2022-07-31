#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 20:42:51 2022

@author: leon
"""


import os
import re
import pandas as pd
import numpy as np
from process_text import load_ticker


def retrieve_price(price_df, target_year_ls, version = "simple"):
    """
    Retrieve price from the price dataframe with the input target
    year list.

    Parameters
    ----------
    price_df : pandas dataframe
        contains ticker, stock price info.
    target_year_ls : list
        a list containing the target years.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    total_sum = 0
    total_count = 0
    price_df['year_date'] = price_df['Date'].apply(lambda x: int(x.split("-")[0]))
    
    if version == "avg":
        # Loop to filter the years in target_year_ls
        for i in target_year_ls:
            temp_df = price_df[price_df['year_date'] == i]
            total_count += len(temp_df)
            total_sum += sum(temp_df['Close'])
            
        if total_count == 0:
            return 0
        price = total_sum / total_count
    elif version == "simple":
        final_year = price_df[price_df['year_date'] == target_year_ls[-1]]
        total_count += len(final_year)
        if total_count == 0:
            return 0
        price = final_year['Close'].iloc[-1]
    return price

def perform_calculate(ticker, gap, horizon,
                          price_load_path = "../price_eps_quarterly",
                          text_load_path = "../stock_text",
                          version = 'simple'):
    """
    input ticker, gap, horizon. gap is the gap between the file report 
    year and the year we use to calculate growth. horizon is the number
    of years we use to calculate mena growth.

    Parameters
    ----------
    ticker : str
        the symbol to represent each company/stock.
    gap : int
        number of years between the file report date and the year used
        in our calculation
    horizon : int
        number of years we use to calculate mean growth rate.
    price_load_path: str
        the path to load the price data corresponding to the ticker
    text_load_path: str
        the path to load the text data corresponding to the ticker
    
    Returns
    -------
    pandas dataframe

    """
    price_filename = ticker + ".csv"
    text_filename = ticker + "_text.csv"
    price_full_path = os.path.join(price_load_path, price_filename)
    text_full_path = os.path.join(text_load_path, text_filename)
    
    if not os.path.isfile(price_full_path):
        print(f"No price data file for {price_filename}")
        return
    
    if not os.path.isfile(text_full_path):
        print(f"No text data file for {text_filename}")
        return
    
    price_df = pd.read_csv(price_full_path, index_col = False)
    text_df = pd.read_csv(text_full_path, index_col = False)
    
    growth_ls = []
    for i in range(len(text_df)):
        cur_year = int(text_df['time'].iloc[i])
        
        # add gap year
        # Notice we add an additional 1, since the text report date
        # is at the end of the year. We want the data to at least "gap" year
        # gap.
        cal_year = cur_year + gap + 1
        # temporary list to save the horizon years.
        temp_ls = []
        for num_year in range(horizon):
            temp_ls.append(cal_year + num_year)
            
        cur_price = retrieve_price(price_df, temp_ls, version = version)
        prev_price = retrieve_price(price_df, [cur_year], version = version)
        cal_growth = cur_price / prev_price
        growth_ls.append(cal_growth)
    
    text_df['growth'] = growth_ls
    return text_df

def loop_calculate(ticker_ls, save_path, save_path2,
                   text_load_path = "../stock_text",
                   price_load_path = "../price_eps_quarterly",
                   gap = 1,
                   horizon = 2,
                   version = 'simple'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(save_path2):
        os.makedirs(save_path2)
    
    if len(os.listdir(save_path)) != 0:
        for f in os.listdir(save_path):
            os.remove(os.path.join(save_path, f))
    
    helper_dic = {}
    for i, tic in enumerate(ticker_ls):
        print("current counter ", i)
        try:
            new_df = perform_calculate(tic, gap = gap, horizon = horizon,
                                       version = version)
            temp_growth_ls = list(new_df['growth'])
        except Exception:
            print("add growth data to the previous text data failed. Continue.")
            continue
        
        save_file_name = tic + "_text_growth.csv"
        save_full_path = os.path.join(save_path, save_file_name)

        new_df.to_csv(save_full_path, index = False)
        
        helper_dic[tic] = temp_growth_ls
    
    helper_df = pd.DataFrame.from_dict(helper_dic, orient = 'index')
    save_full_path2 = os.path.join(save_path2, "ticker_growth.csv")
    helper_df.to_csv(save_full_path2, index = False)
        


     
if __name__ == "__main__":
    temp_price_df = pd.read_csv("../price_eps_quarterly/abmd.csv")    
    temp_price = retrieve_price(temp_price_df, [2022])
        
    
    cal_price_text_df = perform_calculate("a", 1, 2)
        
    temp_year_ls = list(cal_price_text_df['time'])
    temp_growth_ls = list(cal_price_text_df['growth'])
    temp_dict = {"a": temp_growth_ls}
    
    new_temp_df = pd.DataFrame.from_dict(temp_dict, orient = 'index')
    
    ticker_ls = load_ticker("../helper", "ticker_list.txt")
    loop_calculate(ticker_ls, "../stock_text_growth", "../helper")
