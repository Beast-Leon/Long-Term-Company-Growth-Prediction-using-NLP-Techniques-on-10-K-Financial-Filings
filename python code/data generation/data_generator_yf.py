#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 15:38:43 2022

@author: leon
"""
import os
import re
import pandas as pd
import numpy as np
import requests
import yfinance as yf

class DataGenerator_yf():
    # Default to already extracted tickers to ticker.txt
    def __init__(self, load_path, load_name, save_path_dprice,
                 save_path_dprice_helper = None,
                 if_download_price = True, period = "max",
                 interval = "3mo"):
        """

        Parameters
        ----------
        load_path : str
            path to load ticker.txt
        load_name : str
            ticker.txt
        save_path_daily_price : str
            path to save stock daily data
        save_path_daily_price_helper : str, optional
            path to save the mapping of stock ticker
            with each stock daily data length. The default is None.

        if_download_price: bool, optional
            True then perform download stock price. 
        """
        self.load_path = load_path
        self.load_name = load_name
        self.save_path_dprice = save_path_dprice
        self.save_path_dprice_helper = save_path_dprice_helper
        self.if_download_price = if_download_price
        self.period = period
        self.interval = interval
        
        if if_download_price:
            self.perform_download_stock(self.load_path,
                                         self.load_name,
                                         self.save_path_dprice,
                                         self.save_path_dprice_helper,
                                         self.period,
                                         self.interval
                                         )
        

    def load_ticker(self, load_path, file_name):
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
    
    def download_stock(self, ticker, order = "asc",
                             period = "max", interval = "3mo"):
        """
        Input company ticker, retrieve daily stock price data
        from AlphaVantage. Save the retrieved csv file in
        the specific folder. Record each dataframe's length.

        Parameters
        ----------
        ticker : str
            symbol representing each company
            
        order : str, optional
        order can be "asc" or "desc". "asc" indicates the stock
        price dataframe is ordered from the oldest to latest.
        "desc" indicates the stock price dataframe is ordered from
        the latest to the oldest.
        period: str
            valid periods contains
            1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: str
            valid interval contains
            1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

        Returns
        -------
        pandas df, int

        """
        info = yf.Ticker(ticker)
        data = info.history(period = period, interval = interval)
        data = data.dropna()
        if order == "desc":
            data = data.iloc[::-1]
        
        return data, len(data)
    
    
    def perform_download_stock(self, load_path, file_name, save_path,
                                 save_path2 = None, period = "max",
                                 interval = "3mo"):
        """
        Read the ticker.txt file, for each ticker, retrieve the stock
        price data using API from Alpha Vantage. For each downloaded
        stock price dataframe, save to the save_path. Besides, we also 
        record each dataframe's length for future purpose.
    
        Parameters
        ----------
        load_path : str
            the path to load ticker.txt file
        file_name : str
            the input file name
        save_path : str
            the path to save the resulting daily stock csv file.
        api : str, optional
            api to download daily stock price data. The default is API_KEY.
        save_path2 = str, optional
            Default to be None. If not None, this is the path to save
            each csv length data.
        period: str
            valid periods contains
            1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: str
            valid interval contains
            1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        Returns
        -------
        None.
    
        """
        ticker_ls = self.load_ticker(load_path, file_name)
        print("count of tickers are ", len(ticker_ls))
        output_len = {} # Record length of each stock's price dataframe
        
        # Check if the save_path exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # If the save_path contains files, clearing them first.
        if len(os.listdir(save_path)) != 0:
            for f in os.listdir(save_path):
                os.remove(os.path.join(save_path, f))
                
        # Loop through the ticker list, for each list, download data
        for i, tic in enumerate(ticker_ls):
            print("current counter ", i)
            cur_df, cur_len = self.download_stock(tic)
            # cur_len == 0 indicates there is no data
            # corresponding to the current ticker.
            if cur_len == 0:
                continue
            save_file_name = tic +".csv"
            output_len[tic] = cur_len
            save_full_path = os.path.join(save_path, save_file_name)
            cur_df.to_csv(save_full_path)

        
        # If pass the save_path2, save the recorded number of days for 
        # each stock price data into the correponding output length.
        if save_path2:
            if not os.path.exists(save_path2):
                os.makedirs(save_path2)
            if len(os.listdir(save_path2)) != 0:
                for f in os.listdir(save_path2):
                    os.remove(os.path.join(save_path2, f))
                    
            len_df = pd.DataFrame.from_dict(output_len, orient = 'index')
            save_full_path2 = os.path.join(save_path2, "ticker_days.csv")
            len_df.to_csv(save_full_path2)
    
    
    def download_fundamental(ticker):
        """
        download fundamental data for each company,
        including balance, earnings, etc...

        Parameters
        ----------
        ticker : str
            symbol representing each company

        Returns
        -------
        None.

        """
        pass
if __name__ == "__main__":
    """
    import datetime
    from yahoo_earnings_calendar import YahooEarningsCalendar
    
    date_from = datetime.datetime.strptime(
        'May 5 2016  10:00AM', '%b %d %Y %I:%M%p')
    date_to = datetime.datetime.strptime(
        'May 8 2017  1:00PM', '%b %d %Y %I:%M%p')
    yec = YahooEarningsCalendar()
    
    yec.get_earnings_of("box")

    
    import yfinance as yf
    msft = yf.Ticker("MSFT")
    msft.info
    hist = msft.history(period = "max")
    balance = msft.balance_sheet
    cashflow = msft.cashflow
    msft.calendar
    msft.get_balance_sheet(proxy="PROXY_SERVER")

    """
    yf_dg = DataGenerator_yf("../text_data", "ticker.txt", "../stock_quarterly",
                             "../helper", period = "max", interval = "3mo")
    