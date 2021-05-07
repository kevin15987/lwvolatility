#Importing libraries
import ccxt
import numpy as np
import pandas as pd
from datetime import datetime

#Fetching historical data from Gemini
gemini = ccxt.gemini()
since = '01.01.2021' #MM.DD.YYYY


def get_ror(k):
    dt_obj = datetime.strptime(since ,'%m.%d.%Y')
    startdate = dt_obj.timestamp() * 1000
    stock_ohlcv = gemini.fetch_ohlcv("BTC/USD", timeframe = '1d', since = startdate)
    
    df = pd.DataFrame(stock_ohlcv, columns=['date','open','high','low','close','volume'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')   
    df.set_index('date',inplace=True)
    
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    
    fee = 0.0035

    df['ror'] = np.where(df['high'] > df['target'],
                          df['close'] / df['target'] - fee,
                          1)
       
    ror = df['ror'].cumprod()[-2]
    return ror

#Increasing k by 0.01 to see which value returns the highest %
for k in np.arange(0.00,1.00,0.01):
    ror = get_ror(k)
    if ror > 1:
        print((k, ror))
