#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 22:10:37 2022

@author: leon
"""

import os
import re
import pandas as pd
import numpy as np




if __name__ == "__main__":
    data = pd.read_csv('../text_data/risk_factors(title).csv')
    a = pd.unique(data['firm'])
    np.savetxt('ticker.txt', a, fmt='%s')
    
    with open('ticker.txt', 'r') as f:
        lines = f.read()
        contents_split = lines.splitlines()
        print(contents_split)