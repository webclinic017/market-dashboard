from datetime import datetime 
import backtrader as bt
import exchange_calendars as ec
from dateutil.relativedelta import relativedelta

class EOMEffectsStrategy(bt.Strategy):
    params = (
        ('rebalance_monthday', 1),  # Rebalance on the 1st day of the month
        ('allocation_vti', 0.6),    # 60% allocation to VTI
        ('allocation_tlt', 0.4)     # 40% allocation to TLT
    )

    def __init__(self):
        self.spy = self.datas[0]
        self.tlt = self.datas[1]
        self.currentMonth = None

        self.currentTradingDayOfMonth = 0
        self.num_trading_days = 0

        self.exchange = ec.get_calendar('NYSE')
        self.currentPosition = None

    def next(self):
        date = self.data.datetime.date(0)
        self.currentTradingDayOfMonth+=1

        if self.currentMonth != date.month:
            self.currentMonth = date.month
            self.currentTradingDayOfMonth = 0

            start_date = datetime(date.year, date.month, 1)
            end_date = start_date + relativedelta(months=1)
            # Get all the trading days in the current month
            trading_days = self.exchange.sessions_in_range(start_date, end_date)
            # Count the number of trading days in this month
            self.num_trading_days = len(trading_days)
        elif self.currentTradingDayOfMonth == 5:
            # close all positions
            self.order_target_percent(self.tlt, target=0)
            self.order_target_percent(self.spy, target=0)
        elif ((self.num_trading_days - self.currentTradingDayOfMonth) == 5):
            spy_returns = (self.spy.close[0] - self.spy.close[-self.currentTradingDayOfMonth]) / self.spy.close[-self.currentTradingDayOfMonth]
            tlt_returns = (self.tlt.close[0] - self.tlt.close[-self.currentTradingDayOfMonth]) / self.tlt.close[-self.currentTradingDayOfMonth]

            # Buy the under performing asset
            if spy_returns > tlt_returns:
                self.order_target_percent(self.tlt, target=1.0)
                self.currentPosition = 'TLT'
            else:
                self.order_target_percent(self.spy, target=1.0)
                self.currentPosition = 'SPY'
        elif((self.num_trading_days - self.currentTradingDayOfMonth) == 2):
            #last day of the month, close current position and flip long the other
            self.order_target_percent(self.tlt, target=0)
            self.order_target_percent(self.spy, target=0)
            if self.currentPosition == 'TLT':
                self.order_target_percent(self.spy, target=1.0)
            else:
                self.order_target_percent(self.tlt, target=1.0)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        # self.data.datetime.datetime()
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                print(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                print('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

    

