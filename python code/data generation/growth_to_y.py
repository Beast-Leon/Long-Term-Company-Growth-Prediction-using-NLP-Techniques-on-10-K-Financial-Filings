#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:36:43 2022

@author: leon
"""

import os
import re
import pandas as pd
import numpy as np


def categorize_y(actual_growth):
    y = 0
    if actual_growth < 0.75:
        y = 0
    elif 0.75 <= actual_growth < 1.1:
        y = 1
    elif 1.1 <= actual_growth < 1.35:
        y = 2
    elif 1.35 <= actual_growth < 1.75:
        y = 3
    else:
        y = 4
    return y

def convert_growth_to_y(load_path, save_path):
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        # If the save_path contains files, clearing them first.
    if len(os.listdir(save_path)) != 0:
        for f in os.listdir(save_path):
            os.remove(os.path.join(save_path, f))
        
    for f in os.listdir(load_path):
        cur_full_path = os.path.join(load_path, f)
        cur_df = pd.read_csv(cur_full_path, index_col = False)
        cur_df['y'] = cur_df['growth'].apply(lambda x: categorize_y(x))
        
        cur_tic = f.split("_")[0]
        save_file_name = cur_tic + "_text_y.csv"
        save_full_path = os.path.join(save_path, save_file_name)
        cur_df.to_csv(save_full_path, index = False)
        

if __name__ == "__main__":
    convert_growth_to_y("../stock_text_growth", "../stock_text_y")
    
    check = pd.read_csv("../stock_text_y/a_text_y.csv")
