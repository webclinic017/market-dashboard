
import backtrader as bt
import math

# For a month, compare the performance of Stocks vs Bonds.
# Go long the lagger front running the rebalance into end of month
# Optionally go long the winner playing mean reversion the first 5 days of the next month
class VixBasisStrategy(bt.Strategy):
    params = (
        ('long_beginning_of_month', True),  # Long Beginning of Month
        ('front_run_days', 5)
    )

    def __init__(self):
        self.shortvol = self.datas[0]
        self.vix = self.datas[1]
        self.vix3m = self.datas[1]
        self.currentPos = 0
        self.vvol = bt.indicators.StandardDeviation(self.vix, period=60) * math.sqrt(252)
        self.signal = []
        
    def next(self):
        ivts = self.vix.close[0] / self.vix3m.close[0]
        position = VixBasisStrategy.vixBasisStrat(self.vix3m.close[0], ivts, self.vvol)
        self.signal.append(position)

        if position == self.currentPos:
            return
        
        if position == 1:
             self.order_target_percent(self.shortvol, target=0.75, exectype=bt.Order.Market)
        elif position == -1:
            self.order_target_percent(self.shortvol, target=-0.75, exectype=bt.Order.Market)
        else:
            self.close(self.shortvol)

    def plot_vvol(self, axis):
        axis.plot(self.vvol.array)
    
    def plot_signal(self, axis):
        axis.plot(self.signal)

    def plots(self):
        # need to convert these into objects. it takes a matplotlib axis and draws stuff to it
        return [self.plot_vvol, self.plot_signal]

    @staticmethod
    def short_hurdle(vix3m):
        if vix3m < 15:
            return 0.85
        elif vix3m < 17:
            return 0.9
        elif vix3m < 20:
            return 0.95
        elif vix3m < 25:
            return 1
        return 1.1

    @staticmethod
    def vixBasisStrat(vix3m,ivts, vvol):
        shorthurdle = VixBasisStrategy.short_hurdle(vix3m)

        longThreshold = 1.1
        if vvol[0] < 20:
            longThreshold = shorthurdle
        
        if ivts < shorthurdle:
            # long vol
            return 1
        elif ivts > longThreshold:
            #short vol
            return -1
        else:
            return 0

    @staticmethod
    def tickers():
        return ['^SHORTVOL', '^VIX', '^VIX3M' ]

