import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime

def chart(ticker):
    sym_exists = 0
    ticker_map = [['ES=F', 'es'], ['NQ=F', 'nq'], ['YM=F', 'ym'], ['CL=F', 'cl', 'cum'], ['GC=F', 'gc'],
                  ['NG=F', 'ng'], ['^VIX', 'vx']]
    title_map = ['/ES Futures', '/NQ Futures', '/YM Futures', 'Crude Oil Futures', 'Gold Futures',
                 'Nat Gas', '/VX Futures']
    for i, d in enumerate(ticker_map):
        if ticker in d:
            ticker = d[0]
            title = title_map[i]
            sym_exists = 1
            break
    if sym_exists:
        prices = yf.download(ticker, start=datetime.today().strftime('%Y-%m-%d'), interval='5m')

        #create figure
        fig, ax = plt.subplots()
        prices['xTime'] = prices.index.hour.values*60 + prices.index.minute.values
        prices = prices[-100:]
        plt.vlines(x = prices.xTime, ymin=prices.Low, ymax=prices.High, color='silver')
        for index, row in prices.iterrows():
            if row.Close > row.Open:
                plt.vlines(x = row.xTime, ymin=row.Open, ymax=row.Close, color='lime')
            if row.Open > row.Close:
                plt.vlines(x = row.xTime, ymin=row.Close, ymax=row.Open, color='darkred')
        
        #rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right')
        xtick_labels = []
        for index in np.arange(len(prices)):
            if len(prices.index.minute.values.astype(str)[int(index)]) == 1:
                xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                    + ':' + prices.index.minute.values.astype(str)[int(index)]
                                    + '0')
            else:
                xtick_labels.append(prices.index.hour.values.astype(str)[int(index)]
                                    + ':' + prices.index.minute.values.astype(str)[int(index)])
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
    
#aa = chart('vx')