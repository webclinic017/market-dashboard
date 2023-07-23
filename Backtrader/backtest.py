import io
import backtrader as bt

from pandas_datareader import data as pdr
from matplotlib import gridspec

import yfinance as yf
import numpy as np
from backtrader import TimeFrame
import pandas as pd
yf.pdr_override() # <== that's all it takes :-)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run_backtest(strategy, tickers, start, end, title):
    cerebro = bt.Cerebro()

    startcash = 100000
    riskfreerate = 0.02

    for ticker in tickers:
        data = yf.download(ticker, start, end)
        feed = bt.feeds.PandasData(dataname=data)
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
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name="posval")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addstrategy(strategy)

    # Run the backtest
    strats = cerebro.run()

    #https://github.com/webclinic017/BL_model/blob/a1c8abc757d53556c9f728a72190666331bb9f23/moex_black_litterman.py

    # Print final portfolio value
    final_value = cerebro.broker.getvalue()
    print(f"Final portfolio value: ${final_value:.2f}")
    print("Return: ", strats[0].analyzers.returns.get_analysis())
    print("Sharpe Ratio: ", strats[0].analyzers.sharpe.get_analysis())
    print("Drawdown: ", strats[0].analyzers.drawdown.get_analysis())
    print("Active Position Value: ",strats[0].analyzers.posval.get_analysis())

    number_of_years = (pd.to_datetime(end) - pd.to_datetime(start)).days / 365.25
    cagr = (final_value / startcash) ** (1 / number_of_years) - 1
    profits = final_value - startcash
    max_drawdown = strats[0].analyzers.drawdown.get_analysis()['max']['drawdown']


    pyfoliolzer = strats[0].analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = pyfoliolzer.get_pf_items()

    pyfoliolzer = strats[0].analyzers.getbyname('PyFolio')
    
    returns.name = 'Strategy'
    print(returns.head(2))
    

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
    table_vals= [[cagr,2,3,max_drawdown,profits]]

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

    return buf