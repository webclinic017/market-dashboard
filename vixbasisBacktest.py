import yfinance as yf
from datetime import datetime 
from datetime import timedelta
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
import matplotlib
import quantstats as qs

import matplotlib.pyplot as plt
yf.pdr_override()

def backtest():

    end = datetime.today()
    start = end - timedelta(days=3650)

    r = pdr.get_data_yahoo('^SHORTVOL', start, end)['Close']
    vix = pdr.get_data_yahoo('^VIX', start, end)['Close']
    vix3m = pdr.get_data_yahoo('^VIX3M', start, end)['Close']
    ivts = vix / vix3m

    #generate log returns
    rs = r.apply(np.log).diff(1)

    values = pd.DataFrame()
    values['vix'] = vix
    values['vix3m'] = vix3m
    values['ivts'] = ivts

    # return 1 for short vol
    # return 0 for flat
    # return -1 for long vol 
    def vixBasisStrat(x):
        if x['vix3m'] < 15 and x['ivts'] < 0.85:
            return 1
        elif x['vix3m'] < 17 and x['ivts'] < 0.9:
            return 1
        elif x['vix3m'] < 20 and x['ivts'] < 0.95:
            return 1
        elif x['vix3m'] < 25 and x['ivts'] < 1.0:
            return 1
        elif x['vix3m'] >= 25 and x['ivts'] < 1.1:
            return 1
        elif x['ivts'] > 1.1:
            return -1
        return 0


    pos = values.apply(vixBasisStrat, axis=1)

    #fig, ax = plt.subplots(4,1)
    #r.plot(ax=ax[0], title='^SHORTVOL')
    #ivts.plot(ax=ax[1], title='IVTS')
    #pos.plot(ax=ax[2], title='Position')

    #shift 1 day to avoid look-ahead bias
    my_rs = pos.shift(1)*rs

    #calculate returns
    returns = my_rs.cumsum().apply(np.exp)  #.plot(ax=ax[3], title='Strategy Performance')

    qs.reports.html(returns,output=True,download_filename="vixbasis.html")
    return "vixbasis.html"
