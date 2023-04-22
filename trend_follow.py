    
import io
from pandas_datareader import data as pdr
from datetime import timedelta
import yfinance as yf
from datetime import datetime 
from Strategies.MOCPort import MarketOnClosePortfolio
from Strategies.ma_cross import MovingAverageCrossStrategy

import matplotlib.pyplot as plt

yf.pdr_override() # <== that's all it takes :-)

end = datetime.today()
start = end - timedelta(days=3650)
symbol = "aapl"

r = pdr.get_data_yahoo(symbol, start, end) 

# Create a set of random forecasting signals for SPY
rfs = MovingAverageCrossStrategy(symbol, r,short_window=20, long_window=200)
signals = rfs.generate_signals()

# Create a portfolio of SPY
portfolio = MarketOnClosePortfolio(symbol, r, signals, initial_capital=100000.0)
returns = portfolio.backtest_portfolio()

 # Plot two charts to assess trades and equity curve
fig = plt.figure()
fig.patch.set_facecolor('white')     # Set the outer colour to white
ax1 = fig.add_subplot(211,  ylabel='Price in $')

# Plot the AAPL closing price overlaid with the moving averages
r['Close'].plot(ax=ax1, color='r', lw=2.)
signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

# Plot the "buy" trades against AAPL
ax1.plot(signals.loc[signals.positions == 1.0].index, 
            signals.short_mavg[signals.positions == 1.0],
            '^', markersize=10, color='m')

# Plot the "sell" trades against AAPL
ax1.plot(signals.loc[signals.positions == -1.0].index, 
            signals.short_mavg[signals.positions == -1.0],
            'v', markersize=10, color='k')

# Plot the equity curve in dollars
ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
returns['total'].plot(ax=ax2, lw=2.)

# Plot the "buy" and "sell" trades against the equity curve
ax2.plot(returns.loc[signals.positions == 1.0].index, 
            returns.total[signals.positions == 1.0],
            '^', markersize=10, color='m')
ax2.plot(returns.loc[signals.positions == -1.0].index, 
            returns.total[signals.positions == -1.0],
            'v', markersize=10, color='k')

# Plot the figure
#fig.show(block=True)

#buf = io.BytesIO()
plt.tight_layout()
plt.savefig("asdf.png", dpi=300, bbox_inches="tight", format='png')
#buf.seek(0)

