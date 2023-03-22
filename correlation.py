import numpy as np 
import pandas as pd 
# Used to grab the stock prices, with yahoo 
import yfinance as yf
from datetime import datetime 
# To visualize the results 
import matplotlib.pyplot as plt 
import seaborn
from pandas_datareader import data as pdr
yf.pdr_override() # <== that's all it takes :-)


def build():
    start = datetime(2023, 1, 1)
    end = datetime.today()
    symbols_list = ['AAPL', 'F', 'AAL', 'AMZN', 'GOOGL', 'GE', 'TSLA', 'IBM', '^VIX']
    symbols_list.append('VIX')
    #array to store prices
    symbols=[]

    #array to store prices
    symbols=[]
    for ticker in symbols_list:     
        r = pdr.get_data_yahoo(ticker, start, end) 
        # add a symbol column   
        r['Symbol'] = ticker    
        symbols.append(r)
    # concatenate into df
    df = pd.concat(symbols)
    df = df.reset_index()
    df = df[['Date', 'Close', 'Symbol']]
    df.head()
    df_pivot=df.pivot('Date','Symbol','Close').reset_index()
    df_pivot.head()

    corr_df = df_pivot.corr(method='pearson')
    #reset symbol as index (rather than 0-X)
    corr_df.head().reset_index()
    #del corr_df.index.name
    corr_df.head(10)

    plt.figure(figsize=(13, 8))
    seaborn.heatmap(corr_df, annot=True, cmap='RdYlGn')
    plt.savefig('correlation.png')