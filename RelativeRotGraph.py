"""
Relative rotation grpah (RRG) generator

Adapted from personal scripts for Tooters' Market Dashboard

The RRG plots relavtive plots relative momentum vs relative strength of 
  different sector ETF vs the S2PY. Graph default shows the last 15 days with 
  the latest day denoted by the label.
  
Top right quadrant represents 'Leading' sectors
Bottom right is 'cooling'
Bottom left is 'lagging'
and Top left is 'Strengthening'

More information can be found here: https://www.youtube.com/watch?v=TW0Q0lyGIEc&ab_channel=StockCharts

"""
import io
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def RRG(tickers, benchmark, start_date, end_date, lookback, lims=[97, 103]):
    # Download prices from Yahoo Finance
    prices = yf.download(tickers + [benchmark], start=start_date, end=end_date)['Adj Close']
    
    # Normalize prices relative to the first value of the period
    normalized_prices = prices / prices.iloc[0]
    
    # Calculate relative prices to the benchmark
    relative_prices = normalized_prices[tickers].sub(normalized_prices[benchmark], axis=0)
    
    # Calculate rolling mean and standard deviation with a window size of 50 days
    rolling_mean = relative_prices.rolling(window=50).mean()
    rolling_std = relative_prices.rolling(window=50).std()
    
    # Calculate JdK RS ratio
    rs_ratio = 100 + ((relative_prices - rolling_mean) / rolling_std)
    
    # Calculate momentum
    #momentum = normalized_prices[tickers].diff(10)
    momentum = relative_prices[tickers].diff(10)
    # Calculate rolling mean of momentum with a window size of 50 days
    momentum_rolling_mean = momentum.rolling(window=50).mean()
    
    # Calculate JdK RS momentum
    rs_momentum = 100 + ((momentum - momentum_rolling_mean) / momentum.rolling(window=50).std())
    
    # Smooth RS ratio and RS momentum with a rolling mean of 10 days
    rs_ratio = rs_ratio.rolling(window=10).mean()
    rs_momentum = rs_momentum.rolling(window=10).mean()
    
    # Plot the Relative Rotation Graph
    fig, ax = plt.subplots(figsize=(8,8))
    
    # Plot the last 'lookback' values of rs_ratio and rs_momentum for each ticker as a line
    # Add label and dot at most current point
    for ticker in tickers:
        plt.plot(rs_ratio[ticker][lookback:], rs_momentum[ticker][lookback:], label=ticker)
        plt.scatter(rs_ratio[ticker][-1], rs_momentum[ticker][-1])
        ax.text(rs_ratio[ticker][-1], rs_momentum[ticker][-1], ticker, fontsize=12)
    
    # Labels
    plt.xlabel('RS Ratio')
    plt.ylabel('RS Momentum')
    plt.title('Relative Rotation Graph')
    
    # Set limits
    ax.set_xlim(lims[0], lims[1])
    ax.set_ylim(lims[0], lims[1])
    
    # draw lines at x=100 and y=100
    ax.axhline(y=100, color='gray', linestyle='-', linewidth=1)
    ax.axvline(x=100, color='gray', linestyle='-', linewidth=1)
    # Create colored background for each quadrant
    ax.fill_between([100, 105],100,105,alpha=0.1, color='green')
    ax.fill_between([100, 105], 95, 100, alpha=0.1, color='#F9D307')  # yellow
    ax.fill_between([95, 100], 95, 100, alpha=0.1, color='red')  # orange
    ax.fill_between([95, 100], 100, 105, alpha=0.1, color='blue')  # red
    
    # Add legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.text(97.1,102.75,'Strengthening',size=16)
    plt.text(97.1,97.1,'Lagging',size=16)
    plt.text(102.15,97.1,'Cooling',size=16)
    plt.text(102.15,102.75,'Leading',size=16)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
    
start_date = '2022-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')
benchmark = 'SPY'
num_hist = -15

# Define tickers and benchmark
tickers = ['XLP', 'XLE', 'XLF', 'XLRE', 'XLV', 'XLC','XLB','XLI','XLU','XLY','XLK', 'XBI', 'XRT', 'QQQ', 'XHB', 'SMH']
RRG(tickers, benchmark, start_date, end_date, num_hist)


'''
tickers = ['EWZ','EWU','EWW','EWJ','EWG','EWH','EWY','FXI','KWEB']
RRG(tickers, benchmark, start_date, end_date, num_hist, [97,103])

tickers = ['QQQ','IWM','SLY','AVUV', 'MDY', 'FNGS', 'ARKK','MARA']
RRG(tickers, benchmark, start_date, end_date, num_hist)

tickers = ['GLD', 'TLT', 'SLV', 'WEAT', 'BNO', 'CLF', 'URA', 'UNG', 'DBA', 'DBB', 'DBC', 'CORN', 'PALL', 'PPLT']
RRG(tickers, benchmark, start_date, end_date, num_hist)
'''
