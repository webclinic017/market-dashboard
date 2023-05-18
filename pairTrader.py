import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import scipy.stats as stats
import pandas as pd
import io

def spreadMain(ticker_1, ticker_2, num_days):
    data = yf.download([ticker_1,ticker_2], start=(datetime.today()+timedelta(days=num_days)).strftime('%Y-%m-%d'), 
                       end=datetime.today().strftime('%Y-%m-%d'))['Adj Close']
    data.index.name = None
    model = sm.OLS(np.asarray(data[ticker_1.upper()]), sm.add_constant(np.asarray(data[ticker_2.upper()])))
    results = model.fit()
    beta = np.round(results.params[1],2)
    r_sq = np.round(results.rsquared, 3)
    pval = np.round(results.pvalues[1], 3)

    spread = np.asarray(data.get(ticker_1.upper())) - (beta * np.asarray(data.get(ticker_2.upper())))
    adf_stats = adfuller(spread)
    zscores = stats.zscore(spread)

    return(spread, beta, r_sq, pval, np.round(adf_stats[1],3), np.round(zscores[-1],2))


def plot_pairs(spread_l, beta_l, r_sq_l, pval_l, adf_stats_l, zscores_l, 
               spread_s, beta_s, r_sq_s, pval_s, adf_stats_s, zscores_s,
               ticker_1, ticker_2):
    

    table_data = [['Beta', 'R Squared', 'LinReg Pval', 'ADF', 'Z-score'],
              ['180 Days', str(beta_l), str(r_sq_l), str(pval_l), str(adf_stats_l), str(zscores_l)],
              ['60 Days', str(beta_s), str(r_sq_s), str(pval_s), str(adf_stats_s), str(zscores_s)]]
    column_headers = table_data[0]
    row_headers = [row[0] for row in table_data[1:]]
    cell_text = [row[1:] for row in table_data[1:]]
    colors = [['w','w','w','w','w'], ['w','w','w','w','w']]
    
    fig, ax = plt.subplots(3,1)
    fig.suptitle('Pairs trade for '+ticker_1+' and '+ticker_2+'\n'+  \
              'If Z-score < 0: Long '+ticker_1+' and short '+str(beta_s)+' '+ticker_2)
    for i in np.arange(1,3):
        plt.subplot(3,1,i)
        print(i)
        if i == 1:
            spread = spread_l
            for j in np.arange(1,5):
                if j == 1:
                    colors[i-1][j] = critical_val(r_sq_l, [0.90, 0.70], 'gt')
                elif j == 2:
                    colors[i-1][j] = critical_val(pval_l,[0.05, 0.15], 'lt')
                elif j == 3:
                    colors[i-1][j] = critical_val(adf_stats_l,[0.10, 0.25], 'lt')
                else:
                    colors[i-1][j] = critical_val(zscores_l,[-2, -1.35], 'both')
        else:
            spread = spread_s
            for j in np.arange(1,5):
                if j == 1:
                    colors[i-1][j] = critical_val(r_sq_s, [0.90, 0.70], 'gt')
                elif j == 2:
                    colors[i-1][j] = critical_val(pval_s,[0.05, 0.15], 'lt')
                elif j == 3:
                    colors[i-1][j] = critical_val(adf_stats_s,[0.10, 0.25], 'lt')
                else:
                    colors[i-1][j] = critical_val(zscores_s,[-2, -1.35], 'both')

        len_plot = len(spread)
        plt.plot(spread, 'k', linewidth = 1)
        plt.plot([0, len_plot], [np.mean(spread), np.mean(spread)], 'r--', linewidth = 0.5)
        plt.plot([0, len_plot], [np.mean(spread)+np.std(spread),np.mean(spread)+np.std(spread)], 'b--', linewidth = 0.5)
        plt.plot([0, len_plot], [np.mean(spread)-np.std(spread),np.mean(spread)-np.std(spread)], 'b--', linewidth = 0.5)
        plt.plot([0, len_plot], [np.mean(spread)+2*np.std(spread),np.mean(spread)+2*np.std(spread)],'c--', linewidth = 0.5)
        plt.plot([0, len_plot], [np.mean(spread)-2*np.std(spread),np.mean(spread)-2*np.std(spread)],'c--',linewidth = 0.5)
        plt.text(1,np.mean(spread)+np.std(spread),'$\sigma$', color = 'b')
        plt.text(1,np.mean(spread)+2*np.std(spread),'$2\sigma$', color = 'c')
        plt.ylabel('Spread')
        if i == 2: 
            plt.xlabel('Trading Days')
    plt.subplot(3,1,3)
    ax[2].axis('off')
    table = plt.table(cellText=cell_text, cellLoc='center', cellColours=colors,
              rowLabels=row_headers, rowLoc='center',
              colLabels=column_headers, loc='center')
    table.auto_set_font_size(False)
    table.scale(1,1.3)
    table.set_fontsize(10)
    plt.subplots_adjust(hspace=0.4)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
    
    
def critical_val(value, crit_val, check_type):
    if(check_type == 'gt'):
        if value > crit_val[0]:
            color = 'g'
        elif value > crit_val[1]:
            color = 'y'
        else:
            color = 'r'
    elif(check_type == 'lt'):
        if value < crit_val[0]:
            color = 'g'
        elif value < crit_val[1]:
            color = 'y'
        else:
            color = 'r'
    else:
        if value < crit_val[0] or value > np.abs(crit_val[0]):
            color = 'g'
        elif value < crit_val[1] or value > np.abs(crit_val[1]):
            color = 'y'
        else:
            color = 'r'
    return(color)

def scanner():
    #table_data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    table_data = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    #ticker_list = table_data[0]['Symbol']
    ticker_list = table_data[4]['Ticker']
    scan_results = []
    scan_results_f =[]
    count = 0
    num_days = -180
    data = yf.download(ticker_list.values.tolist(), start=(datetime.today()+timedelta(days=num_days)).strftime('%Y-%m-%d'), 
                       end=datetime.today().strftime('%Y-%m-%d'))['Adj Close']
    for a in ticker_list:
        for b in ticker_list[count:]:

            if a != b and not data[a].isnull().values.any() and not data[b].isnull().values.any():
               model = sm.OLS(np.asarray(data[a]), sm.add_constant(np.asarray(data[b])))
               results = model.fit()
               beta = np.round(results.params[1],2)
               r_sq = np.round(results.rsquared, 3)
               pval = np.round(results.pvalues[1], 3)

               spread = np.asarray(data[a]) - (beta * np.asarray(data[b]))
               adf_stats = adfuller(spread)
               zscores = stats.zscore(spread)
               
               if r_sq > 0.8 and pval < 0.1 and adf_stats[1] < 0.15:
                   scan_results.append([a, b])
        count += 1
        print(count)
    
    num_days = -60
    data = yf.download(ticker_list.values.tolist(), start=(datetime.today()+timedelta(days=num_days)).strftime('%Y-%m-%d'), 
                       end=datetime.today().strftime('%Y-%m-%d'))['Adj Close']
    for a in scan_results:
        model = sm.OLS(np.asarray(data[a[0]]), sm.add_constant(np.asarray(data[a[1]])))
        results = model.fit()
        beta = np.round(results.params[1],2)
        r_sq = np.round(results.rsquared, 3)
        pval = np.round(results.pvalues[1], 3)

        spread = np.asarray(data[a[0]]) - (beta * np.asarray(data[a[1]]))
        adf_stats = adfuller(spread)
        zscores = stats.zscore(spread)

        if r_sq > 0.8 and pval < 0.1 and adf_stats[1] < 0.15 and np.abs(zscores[-1]) > 1.5:
            scan_results_f.append(a)
    return(scan_results_f)