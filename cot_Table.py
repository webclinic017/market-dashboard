import pandas as pd
import numpy as np
import os.path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import io

def callAsset(input = 'es'):
    validInput = 0
    lookup = [['SP500', 'es', 'spy', 'spx'], ['NQ', 'nq', 'ndx', 'qqq'], 
              ['Russell', 'rusty', 'iwm', 'rty'], ['Wheat', 'zw', 'wheat'],
              ['Corn', 'zc', 'corn'], ['UltraBond','zb','bonds','tlt','20y'],
              ['10Y', '10y', 'zn'], ['5Y', '5y', 'zf'], ['VIX', 'vx', 'vix', 'vvx'],
              ['BTC', 'btc'], ['OJ', 'oj'], ['Coffee', 'coffee'], ['CL', 'cl', 'cum'],
              ['NatGas', 'ng'], ['Silver', 'slv', 'si'], ['Gold', 'gc', 'gld'],
              ['Copper', 'hg']]

    for i, d in enumerate(lookup):
        if input in d:
            filename = 'https://raw.githubusercontent.com/Poppingfresh/CoT_Repo/main/CoT_'+d[0]+'.csv'
            title_str = d[0]
            validInput = 1
            break
    
    if validInput:
        df = pd.read_csv(filename)
        df['Net NC'] = df['NC Long']-df['NC Short']
        df['Net C'] = df['C Long']-df['C Short']
        df['Net NR'] = df['NR Long']-df['NR Short']
        
        ax1 = df.plot.bar('Index',['Net NC', 'Net C', 'Net NR'], figsize=(20, 10))
        plt.title(title_str)
        plt.xlabel('Date')
        plt.ylabel('Net Position')
        plt.legend(loc='lower left')
    else:
        plt.figure()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# df, title_str = callAsset('cl')
# fig = plotCoT(df, title_str)
            
            