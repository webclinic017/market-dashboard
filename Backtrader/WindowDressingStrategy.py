from datetime import datetime 
import backtrader as bt
import exchange_calendars as ec
from dateutil.relativedelta import relativedelta

# Go long bonds last 5 days of a month, go short bonds first 5 days
class WindowDressingStrategy(bt.Strategy):
    params = (
    )

    def __init__(self):
        self.tlt = self.datas[0]
        self.currentMonth = None

        self.currentTradingDayOfMonth = 0
        self.num_trading_days = 0

        self.exchange = ec.get_calendar('NYSE')

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
        elif self.currentTradingDayOfMonth == 3:
            # close all positions on day 5.  Back trader executes the trade on the next day to avoid "cheating". 
            self.close(self.tlt)
        elif ((self.num_trading_days - self.currentTradingDayOfMonth) == 7):
            # go long bonds last 5 days
            self.order_target_percent(self.tlt, target=0.95, exectype=bt.Order.Market)
        elif(self.isEOM()):
            # advance the day by 2 days so we trade on the last day of the month
            #last day of the month, close current position and flip long the other
            self.order_target_percent(self.tlt, target=-0.95)

    def isEOM(self):
        try:
            date = self.data.datetime.date(2)
            return date.month != self.currentMonth
        except:
            return False

    @staticmethod
    def tickers():
        return ['TLT']

    def plots(self):
        return []

    def strategyData(self):
        return {}
