import io
import os
from flask import Flask
from flask import send_file
from werkzeug.routing import BaseConverter

# Used to grab the stock prices, with yahoo 
import yfinance as yf
from datetime import datetime 
# To visualize the results 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pandas_datareader import data as pdr
from datetime import timedelta
yf.pdr_override() # <== that's all it takes :-)

import correlation
import realizedvol

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

@app.route('/')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)