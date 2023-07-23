import yfinance as yf
from datetime import datetime 
from datetime import timedelta
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
import matplotlib

import matplotlib.pyplot as plt
yf.pdr_override()

end = datetime.today()
start = end - timedelta(days=3650)

r = pdr.get_data_yahoo('AAPL', start, end)['Close']
#generate log returns
rs = r.apply(np.log).diff(1)

# Strategy 
w1 = 5 # short-term moving average window
w2 = 22 # long-term moving average window
ma_x = r.rolling(w1).mean() - r.rolling(w2).mean()
pos = ma_x.apply(np.sign) # +1 if long, -1 if short
fig, ax = plt.subplots(3,1)

ma_x.plot(ax=ax[0], title='Moving Average Cross-Over')
pos.plot(ax=ax[1], title='Position')

#shift 1 day to avoid look-ahead bias
my_rs = pos.shift(1)*rs

#calculate returbs
my_rs.cumsum().apply(np.exp).plot(ax=ax[2], title='Strategy Performance')

plt.show()
