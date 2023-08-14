import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime, timedelta

def chart(ticker, period):
    sym_exists = 0
    ticker_map = [['ES=F', 'es'], ['NQ=F', 'nq'], ['YM=F', 'ym'], ['CL=F', 'cl'], ['GC=F', 'gc'],
                  ['NG=F', 'ng'], ['^VIX', 'vx'], ['CL=F','cum'], ['RTY=F', 'rty'], ['ZB=F', 'zb', '30y'],
                  ['ZN=F', 'zn', '10y'], ['ZF=F', 'zf', '5y'], ['ZT=F', 'zt', '2y'], ['SI=F', 'si'],
                  ['PL=F', 'pl'], ['HG=F', 'hg'], ['PA=F', 'pa'], ['HO=F', 'ho'], ['RB=F', 'rb'],
                  ['ZC=F', 'zc'], ['ZO=F', 'zo'], ['KE=F', 'ke', 'zw'], ['ZR=F', 'zr'], ['ZS=F', 'zs'],
                  ['HE=F', 'he', 'lh'], ['LE=F', 'le'], ['LBS=F', 'lbs', 'lb'], ['OJ=F', 'oj'], 
                  ['DX-Y.NYB', 'dx', 'dxy']]
    title_map = ['/ES Futures', '/NQ Futures', 'The D word you BOOMER', 'Crude Oil Futures', 'Boomer coin (Gold)',
                 'Nat Gas', "Who cares, just sell vol", 'Sweetest lightest crudest cum', 'Rusty (Russell 2000)', '30y Bonds',
                 '10y bonds', '5y bonds', '2y bonds', 'Silver', 'Platinum', 'Copper', 'Palladium',
                 'Heating Oil', 'Gasoline', 'Corn', 'Oats', 'Wheat', 'Rough rice', 'Soy boys', 'Lean Hogs',
                 'Cows', 'Lumber', 'OJ did it', 'AMERICA!']
    for i, d in enumerate(ticker_map):
        if ticker in d:
            ticker = d[0]
            title = title_map[i]
            sym_exists = 1
            break
    if sym_exists:
        if period == '15':
            yf_interval = '15m'
            tdel = 5
        elif period == 'd':
            yf_interval = '1d'
            tdel = 90
        elif period == 'w':
            yf_interval = '1wk'
            tdel = 600
        elif period == 'm':
            yf_interval = '1mo'
            tdel = 2000
        else:
            yf_interval = '5m'
            tdel = 5
        prices = yf.download(ticker, start=(datetime.today()-timedelta(days=tdel)).strftime('%Y-%m-%d'), 
                             interval=yf_interval)
        #create figure
        fig, ax = plt.subplots()
        if yf_interval == '5m':
            prices['xTime'] = prices.index.hour.values*60 + prices.index.minute.values
        else:
            prices['xTime'] = prices.index.values
            
        prices = prices[-60:]
        plt.vlines(x = prices.xTime, ymin=prices.Low, ymax=prices.High, color='silver')
        for index, row in prices.iterrows():
            if row.Close > row.Open:
                plt.vlines(x = row.xTime, ymin=row.Open, ymax=row.Close, color='lime')
            if row.Open > row.Close:
                plt.vlines(x = row.xTime, ymin=row.Close, ymax=row.Open, color='darkred')
        
        #rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right')
        xtick_labels = []
        if yf_interval == '5m' or yf_interval == '15m':
            for index in np.arange(len(prices)):
                if len(prices.index.minute.values.astype(str)[int(index)]) == 1:
                    xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                        + ':' + prices.index.minute.values.astype(str)[int(index)]
                                        + '0')
                else:
                    xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                        + ':' + prices.index.minute.values.astype(str)[int(index)])
        elif yf_interval == '1d':
            for index in np.arange(len(prices)):
                xtick_labels.append(prices.index.month.values.astype(str)[int(index)]+ ' - ' +
                                prices.index.day.values.astype(str)[int(index)])
        else:
            for index in np.arange(len(prices)):
                xtick_labels.append(prices.index.month.values.astype(str)[int(index)]+ ' - ' +
                                prices.index.day.values.astype(str)[int(index)] + ' - ' + 
                                prices.index.year.values.astype(str)[int(index)])
        #display candlestick chart
        plt.xticks(ticks = prices.xTime.values, labels=xtick_labels)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % 10 != 0:
                label.set_visible(False)
        plt.ylabel('Price')
        plt.xlabel('Time')
        plt.title(title)
    else:
        plt.figure()
        
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
    
aa = chart('dxy', 'dxy')