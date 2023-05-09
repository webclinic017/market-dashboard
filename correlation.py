import io
import numpy as np 
import pandas as pd 
# Used to grab the stock prices, with yahoo 
import yfinance as yf
from datetime import datetime 
# To visualize the results 
import matplotlib.pyplot as plt 
import seaborn
from pandas_datareader import data as pdr
from datetime import timedelta
yf.pdr_override() # <== that's all it takes :-)


def build(numDays, symbols_list):
    end = datetime.today()
    start = end - timedelta(days=numDays)

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
    seaborn.heatmap(corr_df, annot=True, cmap='RdYlGn').set(title=f'{numDays} Day Correlation')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def buildChart(numDays,symbols_list):
    end = datetime.today()
    start = end - timedelta(days=numDays)
    sym1 = pdr.get_data_yahoo(symbols_list[0], start, end) 
    sym2 = pdr.get_data_yahoo(symbols_list[1], start, end) 

    sym1['Close'].rolling(50).corr(sym2['Close']).plot()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
