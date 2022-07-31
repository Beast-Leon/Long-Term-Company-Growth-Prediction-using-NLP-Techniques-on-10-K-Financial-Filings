#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 20:11:34 2022

@author: leon
"""
import os
import re
import pandas as pd
import numpy as np

def merge_price_eps(load_path_price, eps_df, save_path,
                    save_path2 = None):
    """
    merge price csv and eps csv according to the date

    Parameters
    ----------
    load_path_price : str
        path to load price files
    eps_df: pandas dataframe
        earnings file
    save_path : str
        path to save files
    save_path2: str
        path to save eps related helper files
    Returns
    -------
    None.

    """
    count_eps = {}
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    for f in os.listdir(load_path_price):
        cur_full_path = os.path.join(load_path_price, f)
        cur_df = pd.read_csv(cur_full_path, index_col = 0)
        cur_symbol = f.split(".")[0]
        
        cur_eps_df = eps_df[eps_df['Symbol'] == cur_symbol.upper()]
        new_df = cur_df.merge(cur_eps_df, on = 'Date', how = 'left')
        
        cur_eps_count = new_df['eps'].count()
        count_eps[cur_symbol] = cur_eps_count
        save_full_path = os.path.join(save_path, f)
        new_df.to_csv(save_full_path)
    
    if save_path2:
        if not os.path.exists(save_path2):
            os.makedirs(save_path2)
                
        eps_count_df = pd.DataFrame.from_dict(count_eps, orient = 'index')
        save_full_path2 = os.path.join(save_path2, "ticker_count_eps.csv")
        eps_count_df.to_csv(save_full_path2)
        
def reconstruct_loop(load_path, save_path):
    """
    Convert date of all files in the load_path 
    to "xxxx-q1", "xxxx-q2"..

    Parameters
    ----------
    load_path : str
        path to load files
    save_path : str
        path to save files

    Returns
    -------
    None.

    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    for f in os.listdir(load_path):
        cur_full_path = os.path.join(load_path, f)
        cur_df = pd.read_csv(cur_full_path)
        new_df = reconstruct_date(cur_df)
        
        save_full_path = os.path.join(save_path, f)
        new_df.to_csv(save_full_path)

def reconstruct_date(df):
    """
    convert date in the format of "xxxx-xx-xx" to
    "xxxx-q1", "xxxx-q2"..
    df should have column of "Date".
    Parameters
    ----------
    df : pandas dataframe
        dataframe with column of date in the format of
        "xxxx-xx-xx"

    Returns
    -------
    pandas dataframe

    """
    df['Date'] = df['Date'].apply(lambda x: reconstruct_date_helper(x))
    return df

def reconstruct_date_helper(date):
    """
    helper of the reconstruct_date function.

    Parameters
    ----------
    date : str
        string with format of "xxxx-xx-xx"

    Returns
    -------
    str

    """
    date = date.split("-")
    year = date[0]
    month = int(date[1])

    cur_qtr = ""
    if 1 <= month <= 3:
        cur_qtr = "q1"
    elif 4 <= month <= 6:
        cur_qtr = "q2"
    elif 7 <= month <= 9:
        cur_qtr = "q3"
    else:
        cur_qtr = "q4"
        
    new_date = year + "-" + cur_qtr
    return new_date

def filter_column_eps(df):
    """
    only select useful columns
    Parameters
    ----------
    df : pandas dataframe
        eps dataframe

    Returns
    -------
    pandas dataframe

    """
    
    new_df = df[['Date', 'Symbol', 'eps']]
    return new_df

if __name__ == "__main__":
    earnings = pd.read_csv("../fundamental_data/earnings_latest.csv")
    earnings = earnings.dropna().reset_index()
    
    new_earnings_df = reconstruct_date(earnings)
    new_earnings_df = filter_column_eps(new_earnings_df)
    
    # Reconstruct date in each stock price csv file
    reconstruct_loop("../stock_quarterly", "../stock_quarterly")
    
    #temp = pd.read_csv("../stock_quarterly/a.csv", index_col = 0)
    
    merge_price_eps("../stock_quarterly", new_earnings_df, "../price_eps_quarterly", "../helper")
    