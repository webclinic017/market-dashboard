import io
import backtrader as bt

from pandas_datareader import data as pdr
from datetime import date

import yfinance as yf
import numpy as np
from backtrader import TimeFrame
import pandas as pd
yf.pdr_override() # <== that's all it takes :-)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def annualized_volatility(dailyReturns):
    returns = np.array(dailyReturns)
    daily_volatility = np.std(returns)

    # Calculate the annualized volatility
    annualized_volatility = daily_volatility * np.sqrt(252)  # Assuming 252 trading days in a year
    return annualized_volatility

# returns a tearsheet of backtest performance
def plot_backtest(strategy, tickers, start, end, title, kwargs):
    cerebro = bt.Cerebro()

    startcash = 100000
    riskfreerate = 0.02

    for ticker in tickers:
        data = yf.download(ticker, start, end)
        feed = bt.feeds.PandasData(dataname=data, name=ticker)
        cerebro.adddata(feed)

    # Set initial portfolio value
    cerebro.broker.setcash(startcash)
    cerebro.broker.set_checksubmit(False)

    # Add the strategy
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,
                        riskfreerate=riskfreerate,
                        timeframe=TimeFrame.Days,
                        annualize=True,
                        _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addstrategy(strategy, **kwargs)

    # Run the backtest
    strats = cerebro.run()

    #https://github.com/webclinic017/BL_model/blob/a1c8abc757d53556c9f728a72190666331bb9f23/moex_black_litterman.py

    # Print final portfolio value
    final_value = cerebro.broker.getvalue()

    number_of_years = (pd.to_datetime(date.today()) - pd.to_datetime(start)).days / 365.25
    cagr = (final_value / startcash) ** (1 / number_of_years) - 1
    profits = final_value - startcash
    max_drawdown = strats[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    sharpe = strats[0].analyzers.sharpe.get_analysis()['sharperatio']


    pyfoliolzer = strats[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = pyfoliolzer.get_pf_items()
    annualized_vol = annualized_volatility(returns)


    portfolio_value = returns.cumsum().apply(np.exp) * startcash
    # Visulize the output
    fig, ax = plt.subplots(3, 1, figsize=[14, 8], gridspec_kw={'height_ratios': [10, 1, 5]})

    # portfolio value
    portfolio_value.plot(ax=ax[0], label='Strategy')
    ax[0].set_ylabel('Portfolio Value')
    ax[0].grid(True)
    ax[0].get_xaxis().label.set_visible(False)
    ax[0].legend()

    col_labels = ['Ann. Return(%)', 'Ann. Sharpe', 'Ann.Volatility(%)', 'Max.DD(%)', 'Tot.Profit($)']
    table_vals= [["{:.2f}".format(cagr*100),"{:.2f}".format(sharpe),"{:.2f}".format(annualized_vol*100),"{:.2f}".format(max_drawdown),"${:,.2f}".format(profits)]]

    ax[1].table(cellText=table_vals,
                     colLabels=col_labels,
                     loc='upper right',
                     edges='open',
                     cellLoc='center')
    ax[1].grid(False)
    ax[1].patch.set_visible(False)
    ax[1].axis('off')

    # daily returns
    returns.plot(ax=ax[2], label='Strategy', alpha=0.5)
    ax[2].set_ylabel('Daily Returns')
    ax[2].grid(True)
    ax[2].get_xaxis().label.set_visible(False)

    fig.subplots_adjust(hspace=0.3, wspace=0.5)
    fig.suptitle(title, fontsize=16)
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    plt.clf()

    # Get the portfolio positions at the end of the backtest
    portfolio_positions = cerebro.broker.positions


    # Print the final portfolio positions and calculate their values
    for data, position in portfolio_positions.items():
        size = position.size
        price = position.price
        value = size * price  # Calculate the position value

        print(f"Data Name: {data._name}, Size: {size}, Price: {price:.2f}, Value: {value:.2f}")

    return buf


# runs the latest positions of the backtest
def run_backtest(strategy, tickers, start, end, kwargs):
    cerebro = bt.Cerebro()
    startcash = 100000

    for ticker in tickers:
        data = yf.download(ticker, start, end)
        feed = bt.feeds.PandasData(dataname=data, name=ticker)
        cerebro.adddata(feed)

    # Set initial portfolio value
    cerebro.broker.setcash(startcash)
    cerebro.broker.set_checksubmit(False)

    cerebro.addstrategy(strategy, **kwargs)

    # Run the backtest
    cerebro.run()

    # Get the portfolio positions at the end of the backtest
    portfolio_positions = cerebro.broker.positions

    pos = []
    for data, position in portfolio_positions.items():
        pos.append({
            'name': data._name,
            'size': position.size,
            'price': position.price
        })

    return pos