import pandas as pd
from Strategies.backtest import Portfolio

class MarketOnClosePortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol        
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()
        
    def generate_positions(self):
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = 100 * self.signals['positions']   # This strategy buys 100 shares
        return positions
                    
    def backtest_portfolio(self):
        pf = pd.DataFrame(index=self.bars.index)
        pf['holdings'] = self.positions.mul(self.bars['Close'], axis='index')
        pf['cash'] = self.initial_capital - pf['holdings'].cumsum()
        pf['total'] = pf['cash'] + self.positions[self.symbol].cumsum() * self.bars['Close']
        pf['returns'] = pf['total'].pct_change()
        return pf