import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import io

def bins():
    dataA = yf.download('^VIX', 
                start=(datetime.today()+timedelta(days=-180)).strftime('%Y-%m-%d'))['Close']
    dataB = yf.download('^VIX3M', 
                start=(datetime.today()+timedelta(days=-180)).strftime('%Y-%m-%d'))['Close']
    
    ratio = dataA/dataB
    df = pd.DataFrame()
    df['Ratio'] = ratio
    df['vix3m'] = dataB
    
    rollback = 3
    
    fig, ax = plt.subplots()
    plt.style.use('default')
    rect = patches.Rectangle((10,0.70),5,0.15,linewidth=1,edgecolor='palegreen',facecolor='palegreen')
    ax.add_patch(rect)
    rect = patches.Rectangle((15,0.70),2,0.20,linewidth=1,edgecolor='palegreen',facecolor='palegreen')
    ax.add_patch(rect)
    rect = patches.Rectangle((17,0.70),3,0.25,linewidth=1,edgecolor='palegreen',facecolor='palegreen')
    ax.add_patch(rect)
    rect = patches.Rectangle((20,0.70),5,0.30,linewidth=1,edgecolor='palegreen',facecolor='palegreen')
    ax.add_patch(rect)
    rect = patches.Rectangle((25,0.70),10,0.40,linewidth=1,edgecolor='palegreen',facecolor='palegreen')
    ax.add_patch(rect)
    plt.plot(df['vix3m'].rolling(rollback).mean()[-21:], df['Ratio'].rolling(rollback).mean()[-21:], '-k')
    plt.plot(df['vix3m'].rolling(rollback).mean()[-1], df['Ratio'].rolling(rollback).mean()[-1], '.k', markersize=10)
    plt.plot(df['vix3m'][-1], df['Ratio'][-1], 'sb', markersize=5)
    plt.plot([10,35],[1.1,1.1], '--r')
    plt.xlabel('VX3M')
    plt.ylabel('VX30/VX3M ratio')
    plt.title('Vol ratios vs 3-month vol')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
    