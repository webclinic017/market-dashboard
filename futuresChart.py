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
                  ['HE=F', 'he', 'lh'], ['LE=F', 'le'], ['LBR=F', 'lbs', 'lb'], ['OJ=F', 'oj'], 
                  ['DX-Y.NYB', 'dx', 'dxy']]
    title_map = ['/ES Futures', '/NQ Futures', 'The D word you BOOMER', 'Crude Oil Futures', 'Boomer coin (Gold)',
                 'Nat Gas', "Who cares, just sell vol", 'Sweetest lightest crudest cum', 'Rusty (Russell 2000)', '30y Bonds',
                 '10y bonds', '5y bonds', '2y bonds', 'Silver', 'Platinum', 'Copper', 'Palladium',
                 'Heating Oil', 'Gasoline', 'Corn', 'Oats', 'Wheat', 'Rough rice', 'Soy boys', "Hurf's Lean Hog",
                 'Cows', " It's big, it's heavy, it's wood", 'OJ did it', 'AMERICA!']
    for i, d in enumerate(ticker_map):
        if ticker in d:
            ticker = d[0]
            title = title_map[i]
            sym_exists = 1
            break
    if sym_exists:
        if period == '15':
            yf_interval = '15m'
            num_slice = -150
            tdel = 5
            lw = 5
        elif period == '1h' or period == 'h':
            yf_interval = '1h'
            tdel = 300
            num_slice = -150
            lw = 3
        elif period == 'd':
            yf_interval = '1d'
            tdel = 200
            num_slice = -250
            lw = 3
        elif period == 'w':
            yf_interval = '1wk'
            tdel = 1000
            num_slice = -250
            lw = 4
        elif period == 'm':
            yf_interval = '1mo'
            tdel = 5000
            num_slice = -250
            lw = 4
        else:
            yf_interval = '5m'
            tdel = 5
            num_slice = -60
            lw = 10
        prices = yf.download(ticker, start=(datetime.today()-timedelta(days=tdel)).strftime('%Y-%m-%d'), 
                             interval=yf_interval)
        #create figure
        fig, ax = plt.subplots(figsize=(20, 10))
        if yf_interval == '5m':
            prices['xTime'] = prices.index.hour.values*60 + prices.index.minute.values
        else:
            prices['xTime'] = prices.index.values
            
        prices = prices[num_slice:]
        plt.vlines(x = prices.xTime, ymin=prices.Low, ymax=prices.High, color='silver', linewidth=lw)
        for index, row in prices.iterrows():
            if row.Close > row.Open:
                plt.vlines(x = row.xTime, ymin=row.Open, ymax=row.Close, color='springgreen', linewidth=lw)
            if row.Open > row.Close:
                plt.vlines(x = row.xTime, ymin=row.Close, ymax=row.Open, color='red', linewidth=lw)
        
        #rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right')
        xtick_labels = []
        xtick_chop = 1
        if yf_interval == '5m' or yf_interval == '15m':
            xtick_chop = 5
            for index in np.arange(len(prices)):
                if len(prices.index.minute.values.astype(str)[int(index)]) == 1:
                    xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                        + ':' + prices.index.minute.values.astype(str)[int(index)]
                                        + '0')
                else:
                    xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                        + ':' + prices.index.minute.values.astype(str)[int(index)])
            plt.xticks(ticks = prices.xTime.values, labels=xtick_labels)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % xtick_chop != 0:
                label.set_visible(False)
        plt.ylabel('Price', fontsize=20)
        plt.yticks(fontsize=16)
        plt.xlabel('Time', fontsize=20)
        plt.xticks(fontsize=16)
        ax.set_facecolor("whitesmoke")
        plt.title(title, fontsize=26)
    else:
        plt.figure()
        
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
    
# aa = chart('dxy', 'dxy')