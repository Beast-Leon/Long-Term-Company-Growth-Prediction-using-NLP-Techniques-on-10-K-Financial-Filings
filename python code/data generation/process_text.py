#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 14:14:42 2022

@author: leon
"""

import os
import re
import pandas as pd
import numpy as np

def load_ticker(load_path, file_name):
    """
    Load ticker text file ticker.txt, return list of tickers.

    Parameters
    ----------
    load_path : str
        data path to load ticker text file

    Returns
    -------
    list

    """
    read_full_path = os.path.join(load_path, file_name)
    with open(read_full_path, 'r') as f:
        lines = f.read()
        contents_split = lines.splitlines()
        
    return contents_split

def load_text(load_full_path):
    """
    Load txt file from the given load_path

    Parameters
    ----------
    load_full_path : 
        the full path to load the corresponding text file.
    Returns
    -------
    str

    """
    text_file = open(load_full_path, "r")
    data = text_file.read()
    text_file.close()
    return data

def find_rf(ticker, rf_map, load_path = "../text_data/10K_riskfactor"):
    """
    Find the risk factor files corresponding to the ticker. Return a dictionary
    containing the ticker, year and risk factor texts.

    Parameters
    ----------
    ticker : str
        a symbol representing a stock
    rf_map : pandas dataframe
        a dataframe with mapping between ticker, date, and risk factor file name.
    load_path: str
        the path to load risk factor related txt file.
    Returns
    -------
    dataframe

    """
    time_ls = []
    rf_ls = []
    tk_ls = [ticker]
    
    cur_rf_map = rf_map[rf_map['firm'] == ticker]
    for i in range(len(cur_rf_map)):
        cur_file = cur_rf_map['filename'].iloc[i]
        cur_date = int(cur_rf_map['time'].iloc[i])
        load_full_path = os.path.join(load_path, cur_file)
        if os.path.isfile(load_full_path):
            cur_txt = load_text(load_full_path)
            rf_ls.append(cur_txt)
            time_ls.append(cur_date)
        else:
            print("There is no corresponding file. Continue.")
    ls_len = len(time_ls)
    tk_ls = tk_ls * ls_len
    out_dict = {"ticker": tk_ls, "time": time_ls, "risk_factor": rf_ls}
    out_df = pd.DataFrame(out_dict)
    return out_df

def find_item1_7(ticker, item1_7_map, input_item, load_path):
    """
    Find the item1 files corresponding to the ticker. Return a dictionary
    containing the ticker, year and item 1 or 7 texts.

    Parameters
    ----------
    ticker : str
        a symbol representing a stock
    item1_7_map : pandas dataframe
        a dataframe with mapping between ticker, date, and item1 and item7 file name
    input_item: str, "1" or "7"
        "1" represent we want item 1. "7" represent we want item 7.
    load_path : str
        the path to load item 1 related txt file.

    Returns
    -------
    dataframe

    """
    time_ls = []
    item_ls = []
    tk_ls = [ticker]
    report_date_ls = []
    
    cur_item_map = item1_7_map[item1_7_map['firm'] == ticker]
    for i in range(len(cur_item_map)):
        if input_item == "1":
            cur_file = cur_item_map['filename'].iloc[i].split(".")[0] + "_item1.txt"
        elif input_item == "7":
            cur_file = cur_item_map['filename'].iloc[i].split(".")[0] + "_item7.txt"
        cur_date = cur_item_map['time'].iloc[i]
        cur_report_date = cur_item_map['report_date'].iloc[i]
        load_full_path = os.path.join(load_path, cur_file)
        if os.path.isfile(load_full_path):
            cur_txt = load_text(load_full_path)
            item_ls.append(cur_txt)
            time_ls.append(cur_date)
            report_date_ls.append(cur_report_date)
            
        else:
            print(f"There is no corresponding file {cur_file}. Continue.")
    ls_len = len(time_ls)
    tk_ls = tk_ls * ls_len
    if input_item == "1":
        out_dict = {"ticker": tk_ls, "time": time_ls, "item1": item_ls, "10K_report_date": report_date_ls}
    elif input_item == "7":
        out_dict = {"ticker": tk_ls, "time": time_ls, "item7": item_ls}
    out_df = pd.DataFrame(out_dict)
    return out_df   


    
def merge_text(rf_df, item1_df, item7_df):
    """
    input ticker, csv of risk factor, dictionary of item1,
    and dictionary of item7. Return a pandas dataframe containing
    date, ticker, risk factor text, MD&A text, business text

    Parameters
    ----------
    rf_df : dataframe
        dataframe of risk factor containing ticker, time, and risk_factor
    item1_df : dataframe
        dataframe of item1 containing ticker, time and item1.
    item7_df : dataframe
        dataframe of item7 containing ticker, time and item7.

    Returns
    -------
    pandas dataframe.

    """
    
    temp_df1 = rf_df.merge(item1_df, on = 'time', how = 'inner')
    temp_df2 = temp_df1.merge(item7_df, on = 'time', how = 'inner')
    final_df = temp_df2.drop(['ticker_x', 'ticker_y'], axis = 1)
    return final_df


def call_merge(ticker_ls, rf_map, item1_7_map, rf_load_path,
               item1_load_path, item7_load_path, save_path,
               save_path2 = None):
    """
    merge risk factor, item1, and item7 texts for all tickers in the
    ticker_ls. Save it to the save_path. We shall save a helper file
    in save_path2.

    Parameters
    ----------
    ticker_ls : TYPE
        DESCRIPTION.
    rf_map : TYPE
        DESCRIPTION.
    item1_7_map : TYPE
        DESCRIPTION.
    rf_load_path : TYPE
        DESCRIPTION.
    item1_load_path : TYPE
        DESCRIPTION.
    item7_load_path : TYPE
        DESCRIPTION.
    save_path : TYPE
        DESCRIPTION.
    save_path2 : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    out_dict = {}
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # If the save_path contains files, clearing them first.
    if len(os.listdir(save_path)) != 0:
        for f in os.listdir(save_path):
            os.remove(os.path.join(save_path, f))
    
    for i, tic in enumerate(ticker_ls):
        rf_df = find_rf(tic, rf_map)
        item1_df = find_item1_7(tic, item1_7_map, "1", item1_load_path)
        item7_df = find_item1_7(tic, item1_7_map, "7", item7_load_path)
        new_df = merge_text(rf_df, item1_df, item7_df)
        cur_len = len(new_df)
        
        # if the resulting file doesn't have item, skip
        if cur_len == 0:
            continue
        out_dict[tic] = cur_len
        save_file_name = tic + "_text.csv"
        save_full_path = os.path.join(save_path, save_file_name)
        new_df.to_csv(save_full_path, index = False)
        
    if save_path2:
        if not os.path.exists(save_path2):
            os.makedirs(save_path2)
        len_df = pd.DataFrame.from_dict(out_dict, orient = 'index')
        save_full_path2 = os.path.join(save_path2, "ticker_num_years.csv")
        len_df.to_csv(save_full_path2, index = False)
                
if __name__ == "__main__":
    
    text_file = open("../text_data/10K_riskfactor/zyxi-0001144204-19-010229.txt", 'r')
    data = text_file.read()
    text_file.close()
    print(data)
    
    
    # Create concise risk factor mapping
    rf = pd.read_csv("../text_data/risk_factors(title).csv")
    unique_file = rf['filename'].unique()
    firm_ls = []
    for i in range(len(unique_file)):
        
        cur_index = rf.index[rf['filename'] == unique_file[i]][0]
        cur_firm = rf.iloc[cur_index]['firm']
        firm_ls.append(cur_firm)
        
    time_ls = []
    for i in range(len(unique_file)):
        cur_index = rf.index[rf['filename'] == unique_file[i]][0]
        cur_time = rf.iloc[cur_index]['time']
        time_ls.append(cur_time)
    new_rf = {"filename": list(unique_file), "firm": firm_ls, "time": time_ls}
    new_rf = pd.DataFrame(new_rf)
    
    new_rf.to_csv("../helper/ticker_rf_mapping.csv")
    
    
    # Create concise business  mapping
    item1_7_df = pd.read_csv("../text_data/ticker_item1_7_mapping.csv", index_col = 0)
    item1_7_df = item1_7_df.dropna()
    con_item1_7 = item1_7_df[['filename', 'tic_in_comp', 'fdate', 'report_date']]    
    
    con_item1_7.columns = ['filename', 'firm', 'time', 'report_date']
    con_item1_7['firm'] = con_item1_7['firm'].apply(lambda x: x.lower())
    con_item1_7['time'] = con_item1_7['time'].apply(lambda x: int(x.split("-")[0]))
    con_item1_7.to_csv("../helper/ticker_item1_7_mapping.csv")    
    
    
    temp_file = con_item1_7['filename'].iloc[0]
    
    temp_file = temp_file.split(".")   
    
    temp_item7 = temp_file[0] + "_item7.txt"    
    
    temp_full_path = os.path.join("../text_data/item7MD&A", temp_item7)
    
    os.path.isfile(temp_full_path)
    
    rf_map = pd.read_csv("../helper/ticker_rf_mapping.csv", index_col = False)
    temp_rf = find_rf("a", rf_map)
    
    item1_7_map = pd.read_csv("../helper/ticker_item1_7_mapping.csv", index_col = False)
    temp_item1 = find_item1_7("a", item1_7_map, "1", "../text_data/item1business")
    temp_item7 = find_item1_7("a", item1_7_map, "7", "../text_data/item7MD&A")
    
    new1 = temp_rf.merge(temp_item1, on = 'time', how = 'inner')
    new2 = new1.merge(temp_item7, on = 'time', how = 'inner')
    new2.columns
    final_df = new2.drop(['ticker_x', 'ticker_y'], axis = 1)
    
    ticker_ls = load_ticker("../helper", "ticker_list.txt")
    call_merge(ticker_ls, rf_map, item1_7_map, "../text_data/10K_riskfactor",
               "../text_data/item1business", "../text_data/item7MD&A", "../stock_text",
               "../helper")