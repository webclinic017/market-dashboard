import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta

def ivCone(ticker="SPY", start_date=(datetime.today()+timedelta(days=-365)).strftime('%Y-%m-%d'),
           end_date=datetime.today().strftime('%Y-%m-%d')):
    
  # People will use the incorrect date format because they suck
  for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%m-%d-%Y'):
    try:
      datetime.strptime(start_date, fmt)
    except ValueError:
      pass
    else:
      start_date = datetime.strptime(start_date, fmt).strftime('%Y-%m-%d')
    
    try:
      datetime.strptime(end_date, fmt)
    except ValueError:
      pass
    else:
      end_date = datetime.strptime(end_date, fmt).strftime('%Y-%m-%d')
      
  windows = [7, 14, 30, 45, 60, 90, 120]
  quantiles = [0.25, 0.75]
  min_ = []
  max_ = []
  median = []
  top_q = []
  bottom_q = []
  realized = []

  data = yf.download(ticker, start=start_date, end=end_date)
  
  for window in windows:
    log_return = (data["Close"] / data["Close"].shift(1)).apply(np.log)
    estimator = log_return.rolling(window=window, center=False).std() * math.sqrt(252)
    # append the summary stats to a list
    min_.append(estimator.min())
    max_.append(estimator.max())
    median.append(estimator.median())
    top_q.append(estimator.quantile(quantiles[1]))
    bottom_q.append(estimator.quantile(quantiles[0]))
    realized.append(estimator[-1])
 
  # create the plots on the chart
  plt.figure(ticker)
  plt.plot(windows, min_, "-o", linewidth=1, label="Min")
  plt.plot(windows, max_, "-o", linewidth=1, label="Max")
  plt.plot(windows, median, "-o", linewidth=1, label="Median")
  plt.plot(windows, top_q, "-o", linewidth=1, label=f"{quantiles[1] * 100:.0f} Pctile")
  plt.plot(windows, bottom_q, "-o", linewidth=1, label=f"{quantiles[0] * 100:.0f} Pctile")
  plt.plot(windows, realized, "ro-.", linewidth=1, label="Realized")

  # set the x-axis labels
  plt.xticks(windows)
  plt.title('RVol/IVol Estimate for $'+ticker+'\n from '+start_date+' to '+end_date)
  plt.xlabel('Days to Expiration')
  plt.ylabel('Volatility')
  # format the legend
  plt.legend(loc="upper right", ncol=3)
  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  return buf
