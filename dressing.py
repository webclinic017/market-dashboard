import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime, timedelta

def dressing(ticker = 'SPY', start_date = (datetime.today()+timedelta(days=-365)).strftime('%Y-%m-%d'),
             end_date = datetime.today().strftime('%Y-%m-%d')):

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
      
  # Get price data
  stock_data = yf.download(ticker, start=start_date, end=end_date)

  logAdjDiff = np.log(np.asarray(stock_data['Adj Close'][1:])/np.asarray(stock_data['Adj Close'][0:-1]))

  logAdjDiff = np.insert(logAdjDiff,0,np.nan)
  #dayOfMon = np.asarray(stock_data.index.day)

  avg_data = np.zeros([2,31])
  med_data = np.zeros([2,31])
  #min_data = np.zeros([2,31])
  #max_data = np.zeros([2,31])

  avg_data[0,0:31] = range(1,32)
  med_data[0,0:31] = range(1,32)
  #min_data[0,0:31] = range(1,32)
  #max_data[0,0:31] = range(1,32)

  trade_dayOfMon = np.zeros(logAdjDiff.shape[0])

  #nyse = mcal.get_calendar('NYSE')

  for i in range(int(start_date[0:4]),int(end_date[0:4])+1):
  #  for j in range(int(start_date[5:7]),int(end_date[5:7])+1):
    for j in np.arange(1,13):
      trade_dayOfMon[np.where((stock_data.index.year == i) & (stock_data.index.month == j))] = \
       (np.arange(1,np.asarray(np.where((stock_data.index.year == i) & (stock_data.index.month == j))).size+1))


  for i in range(0,23):
    avg_data[1,i] = np.nanmean(logAdjDiff[trade_dayOfMon == i+1])
    med_data[1,i] = np.nanmedian(logAdjDiff[trade_dayOfMon == i+1])
    #min_data[1,i] = np.nanmin(logAdjDiff[trade_dayOfMon == i+1])
    #max_data[1,i] = np.nanmax(logAdjDiff[trade_dayOfMon == i+1])
  
  fig, ax = plt.subplots()
  plt.style.use('default')
  plt.bar(avg_data[0,:]-0.2, avg_data[1,:], width=0.4, color='b')
  plt.bar(med_data[0,:]+0.2, med_data[1,:], width=0.4, color='k')
  plt.legend(['Average','Median'])
  plt.xlim([-0.5, 25])
  ax.set_xlabel('Start of Month Trading Days')
  ax.set_ylabel('log return')
  ax.set_title('Daily returns for ' + ticker + " \n From " + start_date + " to " + str(stock_data.index[-1])[0:10])
  '''
  fig, ax = plt.subplots()
  plt.bar(min_data[0,:]-0.2, min_data[1,:], width=0.4, color='tab:orange')
  plt.bar(max_data[0,:]+0.2, max_data[1,:], width=0.4, color='g')
  plt.legend(['Min','Max'])
  ax.set_xlabel('Start of Month Trading Days') 
  ax.set_ylabel('log return')
  ax.set_title('Daily returns for ' + ticker + " \n From " + start_date + " to " + str(stock_data.index[-1])[0:10])
  '''
  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  return buf
