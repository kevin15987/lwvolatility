#Importing libraries
import ccxt
import numpy as np
import pandas as pd
from datetime import datetime

#Fetching historical data from Gemini
since = '01.01.2021' #MM.DD.YYYY
gemini = ccxt.gemini()
dt_obj = datetime.strptime(since ,'%m.%d.%Y')
since = dt_obj.timestamp() * 1000
stock_ohlcv = gemini.fetch_ohlcv("BTC/USD", timeframe = '1d', since = since)
df = pd.DataFrame(stock_ohlcv, columns=['date','open','high','low','close','volume'])
df['date'] = pd.to_datetime(df['date'], unit='ms')   
df.set_index('date',inplace=True)

#Back testing equation. For backtesting purpose, assume you start off with 1 BTC
k = 0.68
df['range'] = (df['high'] - df['low']) * k
df['target'] = df['open'] + df['range'].shift(1)

#Fee assumption
fee = 0.0035

#To Buy or Not To Buy
df['ror'] = np.where(df['high'] > df['target'],
                      df['close'] / df['target'] - fee,
                      1)
#Compound Return
df['hpr'] = df['ror'].cumprod()
#Drawdown
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
#Max Drawdown
print(df['dd'].max())
df.to_excel("backtesting.xlsx")