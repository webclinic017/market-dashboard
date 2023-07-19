from datetime import datetime 
import backtrader as bt
import pandas as pd
from pandas_datareader import data as pdr
from datetime import timedelta
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

class RebalanceStrategy(bt.Strategy):
    params = (
        ('rebalance_monthday', 1),  # Rebalance on the 1st day of the month
        ('allocation_vti', 0.6),    # 60% allocation to VTI
        ('allocation_tlt', 0.4)     # 40% allocation to TLT
    )

    def __init__(self):
        self.vti = self.datas[0]
        self.tlt = self.datas[1]
        self.counter = 0

    def next(self):
        #self.data.datetime.date(0) returns the date of the data.  Need to get the last day of the month
        if self.counter % 30 == 0:
            self.rebalance_portfolio()

        self.counter += 1

    def rebalance_portfolio(self):
        self.order_target_percent(self.vti, target=self.params.allocation_vti)
        self.order_target_percent(self.tlt, target=self.params.allocation_tlt)


def run_backtest():
    cerebro = bt.Cerebro()

    end = datetime.today()
    start = end - timedelta(days=3650)
    vti_data = yf.download('SPY', start, end)
    tlt_data = yf.download('TLT', start, end)

    # Create backtrader data feeds
    vti_feed = bt.feeds.PandasData(dataname=vti_data)
    tlt_feed = bt.feeds.PandasData(dataname=tlt_data)

    # Add data feeds to cerebro
    cerebro.adddata(vti_feed)
    cerebro.adddata(tlt_feed)

    # Set initial portfolio value
    cerebro.broker.setcash(100000)

    # Add the strategy
    cerebro.addstrategy(RebalanceStrategy)

    # Run the backtest
    cerebro.run()

    # Print final portfolio value
    final_value = cerebro.broker.getvalue()
    print(f"Final portfolio value: ${final_value:.2f}")
    return final_value

if __name__ == '__main__':
    run_backtest()
