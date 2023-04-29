
import datetime
from pandas_datareader import data as pdr
from datetime import timedelta
import yfinance as yf
from datetime import datetime 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from realizedvol import yang_zhang

yf.pdr_override() # <== that's all it takes :-)

import seaborn as sns

end = datetime.today()
start = end - timedelta(days=36500)
vix3m = pdr.get_data_yahoo('^VIX3M', start, end) 
vixStart = vix3m.index[0]

vix = pdr.get_data_yahoo('^VIX', vixStart, end) 
spy = pdr.get_data_yahoo('SPY', vixStart, end) 

plt.style.use('dark_background')

difference = pd.DataFrame()

difference['diff'] = vix['Close'].divide(vix3m['Close'])
difference['z_score'] = (difference - difference.mean())/difference.std()
merged_df = pd.merge(difference, spy, on='Date')

merged_df['forward_returns'] = merged_df['Close'].shift(-90) / merged_df['Close'] - 1
merged_df['year'] = merged_df.index.year

merged_df['realized_vol'] = yang_zhang(spy,30)
merged_df['rvol_z_score'] = (merged_df['realized_vol'] - merged_df['realized_vol'].mean())/merged_df['realized_vol'].std()

merged_df['bin'] = pd.cut(merged_df['rvol_z_score'], [-10, 0, 10], labels=['low', 'high'])

# Plot sepal width as a function of sepal_length across days
g = sns.lmplot(
    data=merged_df,
    x="forward_returns", y="z_score",
    hue="bin",
    height=5
)

# Use more informative axis labels than are provided by default
g.set_axis_labels("Spy 3mo fwd returns", "VIX/VIX3M zscore")

plt.savefig("images/plt.png", format='png')
plt.clf()

merged_df['z_score'].plot(figsize=(20,10)).get_figure().savefig("images/zscore.png", format='png')
plt.clf()
merged_df['realized_vol'].plot(figsize=(20,10)).get_figure().savefig("images/rvol.png", format='png')
plt.clf()
merged_df['rvol_z_score'].plot(figsize=(20,10)).get_figure().savefig("images/rvol_zscore.png", format='png')


