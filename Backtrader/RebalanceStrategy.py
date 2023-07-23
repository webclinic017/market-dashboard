import backtrader as bt

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
        if self.counter % 25 == 0:
            self.rebalance_portfolio()

        self.counter += 1

    def rebalance_portfolio(self):
        self.order_target_percent(self.vti, target=self.params.allocation_vti)
        self.order_target_percent(self.tlt, target=self.params.allocation_tlt)
