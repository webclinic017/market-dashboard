import yfinance as yf
from datetime import datetime 
from datetime import timedelta
from pandas_datareader import data as pdr
yf.pdr_override()
    

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA

class RebalanceEffects(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 5)
        self.ma2 = self.I(SMA, price, 50)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


def rebalance_backtest():
    end = datetime.today()
    start = end - timedelta(days=3650)
    spy = pdr.get_data_yahoo('SPY', start, end) 


    bt = Backtest(spy, RebalanceEffects, commission=.002,
                exclusive_orders=True)
    stats = bt.run()
    bt.plot(open_browser=False, filename='RebalanceEffects.html')
    return 'RebalanceEffects.html'