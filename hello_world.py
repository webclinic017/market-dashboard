import io
import os
from flask import Flask
from flask import send_file
from flask import jsonify
from werkzeug.routing import BaseConverter
import scipy.stats as stats
import pandas as pd 
import exchange_calendars as ec
import Backtrader.backtest
from Backtrader.RebalanceStrategy import RebalanceStrategy
from Backtrader.EOMEffects import EOMEffectsStrategy
from Backtrader.vixbasis import VixBasisStrategy
from Backtrader.WindowDressingStrategy import WindowDressingStrategy

import json

# Used to grab the stock prices, with yahoo 
import yfinance as yf
from datetime import datetime 
# To visualize the results 
import matplotlib

from RelativeRotGraph import RRG
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pandas_datareader import data as pdr
from datetime import timedelta
yf.pdr_override() # <== that's all it takes :-)

import correlation
import realizedvol
import dressing
import volCone
# import pairTrader
import futuresChart

class ListConverter(BaseConverter):

    def to_python(self, value):
        return [str(x) for x in value.split(',')]

    def to_url(self, value):
        return ','.join(str(x) for x in value)

app = Flask(__name__)
app.url_map.converters['list'] = ListConverter

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/correlation')
@app.route('/correlation/<int:days>')
@app.route('/correlation/<int:days>/<list:symbols>')
def correlationChart(days=30, symbols=['SPY', 'QQQ', 'IWM', 'TLT', 'GLD', 'USO', 'UUP', '^VIX', 'BTC-USD', 'ETH-USD']):
    plt.style.use('dark_background')
    if(len(symbols) == 2):
        buf = correlation.buildChart(days, symbols)
    else:
        buf = correlation.build(days,symbols)
    plt.clf()
    return send_file(buf, mimetype='image/png')


@app.route('/realized_vol/<ticker>')
def realized_vol(ticker):
    end = datetime.today()
    start = end - timedelta(days=365)
    r = pdr.get_data_yahoo(ticker, start, end) 
    buf = io.BytesIO()
    plt.style.use('dark_background')
    plt.title(f'30 Day Rolling Realized Vol of {ticker.upper()}')
    realizedvol.yang_zhang(r).plot().get_figure().savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/realized_vol_term/<ticker>')
def realized_vol_term(ticker):
    end = datetime.today()
    start = end - timedelta(days=365)
    r = pdr.get_data_yahoo(ticker, start, end) 
    buf = io.BytesIO()
    plt.style.use('dark_background')
    plt.title(f'Realized Vol of {ticker.upper()}')
    
    realizedvol.yang_zhang(r,9).plot(label="9d")
    realizedvol.yang_zhang(r,30).plot(label="30d")
    plot = realizedvol.yang_zhang(r,90).plot(label="90d")
    plt.legend(loc="upper left")
    plot.get_figure().savefig(buf, format='png')
    
    plt.clf()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/vrp')
def vrp():
    end = datetime.today()
    start = end - timedelta(days=3650)
    r = pdr.get_data_yahoo('^SPX', start, end)
    vix = pdr.get_data_yahoo('^VIX', start, end)
   
    plt.style.use('dark_background')
    plt.title(f'Implied Vol Premium SPX and VIX 30 day')

    rvol = realizedvol.yang_zhang(r,30).mul(100)
    df = vix['Close'] - rvol
    plot = df.plot(label='VRP')

    plt.legend(loc="upper left")

    buf = io.BytesIO()
    plot.get_figure().savefig(buf, format='png')
    
    plt.clf()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/vrp/json')
def vrp_json():
    end = datetime.today()
    start = end - timedelta(days=3650)
    r = pdr.get_data_yahoo('^SPX', start, end)
    vix = pdr.get_data_yahoo('^VIX', start, end)
   
    rvol = realizedvol.yang_zhang(r,30).mul(100)
  
    df = vix['Close'] - rvol
    zscore = stats.zscore(df,nan_policy='omit')
    return jsonify(d30 = realizedvol.rvol_to_json(df), d30Zscore = realizedvol.rvol_to_json(zscore))
    
@app.route('/realized_vol_term/json/<ticker>')
def realized_vol_term_json(ticker):
    end = datetime.today()
    start = end - timedelta(days=365)
    r = pdr.get_data_yahoo(ticker, start, end) 
    
    d9rvol = realizedvol.rvol_to_json(realizedvol.yang_zhang(r,9))
    d30rvol = realizedvol.rvol_to_json(realizedvol.yang_zhang(r,30))
    d90rvol = realizedvol.rvol_to_json(realizedvol.yang_zhang(r,90))

    return jsonify(
        d9 = d9rvol,
        d30 = d30rvol,
        d90 = d90rvol
    )

@app.route('/rrg')
@app.route('/rrg/<rrg_set>')
def rrg(rrg_set):
    start_date = (datetime.today()+timedelta(days=-365)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')
    benchmark = 'SPY'
    num_hist = -10
    plt.style.use('default')
    # Define tickers and benchmark
    if rrg_set == '1' or not rrg_set:
        tickers = ['XLP', 'XLE', 'XLF', 'XLRE', 'XLV', 'XLC','XLB','XLI','XLU','XLY','XLK', 'XBI', 'XRT', 'QQQ', 'XHB', 'SMH']
    elif rrg_set == '2':
        tickers = ['GLD', 'TLT', 'SLV', 'WEAT', 'USO', 'CLF', 'URA', 'UNG', 'CORN', 'PALL', 'PPLT']
    elif rrg_set == '3':
        tickers = ['EWZ','EWU','EWW','EWJ','EWG','EWH','EWY','FXI','KWEB']
    else:
        tickers = ['XLP', 'XLE', 'XLF', 'XLRE', 'XLV', 'XLC','XLB','XLI','XLU','XLY','XLK', 'XBI', 'XRT', 'QQQ', 'XHB', 'SMH']
        
    buf = RRG(tickers, benchmark, start_date, end_date, num_hist)
    plt.clf()
    return send_file(buf, mimetype='image/png')

@app.route('/dressingMain')
@app.route('/dressingMain/<ticker>')
@app.route('/dressingMain/<ticker>/<start_date>')
@app.route('/dressingMain/<ticker>/<start_date>/<end_date>')
def dressingMain(ticker = 'SPY', start_date = (datetime.today()+timedelta(days=-365)).strftime('%Y-%m-%d'), end_date = datetime.today().strftime('%Y-%m-%d')):
    buf = dressing.dressing(ticker, start_date, end_date)
    plt.clf()
    return send_file(buf, mimetype='image/png')
    
@app.route('/IVCone')
@app.route('/IVCone/<ticker>')
@app.route('/IVCone/<ticker>/<start_date>')
@app.route('/IVCone/<ticker>/<start_date>/<end_date>')
def IVCone(ticker = 'SPY', start_date = (datetime.today()+timedelta(days=-365)).strftime('%Y-%m-%d'), end_date = datetime.today().strftime('%Y-%m-%d')):
    buf = volCone.ivCone(ticker, start_date, end_date)
    plt.clf()
    return send_file(buf, mimetype='image/png')
    
# @app.route('/pairsMaster')
# @app.route('/pairsMaster/<ticker_1>')
# @app.route('/pairsMaster/<ticker_1>/<ticker_2>')
# def pairsMaster(ticker_1, ticker_2):
#     if ticker_1 == ticker_2:
#         return
#     if ticker_1 == 'scan' and ticker_2 == 'active':
#         #Scans Nasdaq 100 stocks for potential pairs that meet certain criteria
#         scan_results = pairTrader.scanner()
#         plt.table(scan_results)
#         plt.title('Scan Results')
#         plt.axis('off')
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png')
#         buf.seek(0)
#         plt.clf()
#         return send_file(buf, mimetype='image/png')
    
#     spread_l, beta_l, r_sq_l, pval_l, adf_stats_l, zscores_l = pairTrader.spreadMain(ticker_1, ticker_2, -180)
#     spread_s, beta_s, r_sq_s, pval_s, adf_stats_s, zscores_s = pairTrader.spreadMain(ticker_1, ticker_2, -60)
#     buf = pairTrader.plot_pairs(spread_l, beta_l, r_sq_l, pval_l, adf_stats_l, zscores_l,
#                                 spread_s, beta_s, r_sq_s, pval_s, adf_stats_s, zscores_s,
#                                 ticker_1, ticker_2)
#     plt.clf()
#     return send_file(buf, mimetype='image/png')

@app.route('/vixBasis')
def vix_basis():
    end = datetime.today()
    start = end - timedelta(days=3650)
    vix = pdr.get_data_yahoo('^VIX', start, end)
    vix3m = pdr.get_data_yahoo('^VIX3M', start, end)

    ivts = vix['Close'] / vix3m['Close']
    vvol = realizedvol.standard_deviation(vix, 60)

    return jsonify(
        vvol = realizedvol.rvol_to_json(vvol, 'Close'),
        ivts = realizedvol.rvol_to_json(ivts, 'Close')
    )

@app.route('/stock_bond')
def prices():
    end = datetime.today()
    start = end - timedelta(days=3000)
 
    spy = pdr.get_data_yahoo('SPY', start, end)
    tlt = pdr.get_data_yahoo('TLT', start, end)

    spy_monthly_data = spy.resample('M').ffill()
    tlt_monthly_data = tlt.resample('M').ffill()

    spy_monthly_returns = spy_monthly_data['Close'].pct_change().dropna()
    tlt_monthly_returns = tlt_monthly_data['Close'].pct_change().dropna()

    # Combine Date, TLT monthly returns, and SPY monthly returns
    combined_data = []
    for date, tlt_return, spy_return in zip(tlt_monthly_returns.index, tlt_monthly_returns, spy_monthly_returns):
        data = {'Date': date.strftime('%Y-%m-%d'), 'TMF': tlt_return, 'UPRO': spy_return}
        combined_data.append(data)
    
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Filter the DataFrame based on the current month
    filtered_df = spy[(spy.index.month == current_month) & (spy.index.year == current_year)]
    tradingDay = len(filtered_df.index)

    # calculate the number of trading days in this current month
    # we need to know when there are 5 trading days left in the month
    # Get the calendar for a specific exchange
    exchange = ec.get_calendar('NYSE')

    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Get the start and end dates of the current month
    start_date = datetime(current_year, current_month, 1)
    end_date = datetime(current_year, current_month + 1, 1)

    # Get all the trading days in the current month
    trading_days = exchange.sessions_in_range(start_date, end_date)

    # Count the number of trading days
    num_trading_days = len(trading_days)

    stockBondJson = { "returns": combined_data, "currentTradingDay": tradingDay, "tradingDaysInMonth": num_trading_days}
    # Convert combined_data to a JSON array
    json_data = json.dumps(stockBondJson)

    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    
    return response

@app.route('/backtest')
def backtestThings():
    buf = Backtrader.backtest.run_backtest(RebalanceStrategy, ['SPY','TLT'], start='2013-01-01', end='2100-01-01', title='60-40 Rebalance SPY, TLT')        
    return send_file(buf, mimetype='image/png')

    
# need to configure the args and if we want the image or the positons
@app.route('/backtest/eom')
@app.route('/backtest/eom/<mode>')
def backtestEOM(mode="bom"):
    kwargs = {
        'long_beginning_of_month': (mode == 'bom')
    }
    buf = Backtrader.backtest.plot_backtest(EOMEffectsStrategy, ['SPY','TLT'], start='2013-01-01', end='2100-01-01', title='End of Month Effects', kwargs=kwargs)        
    return send_file(buf, mimetype='image/png')

@app.route('/backtest/execute/eom')
@app.route('/backtest/execute/eom/<mode>')
def executeBacktestEOM(mode="bom"):
    kwargs = {
        'long_beginning_of_month': (mode == 'bom')
    }
    data = Backtrader.backtest.run_backtest(EOMEffectsStrategy, ['SPY','TLT'], start='2023-01-01', end='2100-01-01', kwargs=kwargs)        
    json_data = json.dumps(data)

    return app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )

@app.route('/backtest/vixbasis')
def backtestVixBasis():
    kwargs = {
    }
    buf = Backtrader.backtest.plot_backtest(VixBasisStrategy, VixBasisStrategy.tickers(), start='2013-01-01', end='2100-01-01', title='VIX Basis', kwargs=kwargs)        
    return send_file(buf, mimetype='image/png')

@app.route('/backtest/execute/vixbasis')
def executeBacktestVixBasis():
    kwargs = {
    }
    data = Backtrader.backtest.run_backtest(VixBasisStrategy, VixBasisStrategy.tickers(), start='2023-01-01', end='2100-01-01', kwargs=kwargs)          
    json_data = json.dumps(data)

    return app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )

@app.route('/backtest/windowdressing')
def backtestWindowDressing():
    kwargs = {
    }
    buf = Backtrader.backtest.plot_backtest(WindowDressingStrategy, WindowDressingStrategy.tickers(), start='2013-01-01', end='2100-01-01', title='VIX Basis', kwargs=kwargs)        
    return send_file(buf, mimetype='image/png')

@app.route('/backtest/execute/windowdressing')
def executeWindowDressing():
    kwargs = {
    }
    data = Backtrader.backtest.run_backtest(WindowDressingStrategy, WindowDressingStrategy.tickers(), start='2023-01-01', end='2100-01-01', kwargs=kwargs)          
    json_data = json.dumps(data)

    return app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    
@app.route('/futureschart/<ticker>/<period>')
def futureschart(ticker = 'es', period = '5'):
    plt.style.use('default')
    buf = futuresChart.chart(ticker, period)
    print(type(buf))
    return send_file(buf, mimetype='image/png')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


    