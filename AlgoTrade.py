#Importing libraries
import gemini
import ccxt
import pandas as pd
import time
import datetime
from datetime import timedelta
r = gemini.PrivateClient("PUBLICACCOUNT", "SECRETKEY")

##Get live BTC price 
#while True:
#  price = cryptocompare.get_price('BTC', currency = 'USD')
#  print (price)
#  time.sleep(0.2)

#Fetching data from Gemini
gemini = ccxt.gemini()
ticker = "BTC/USD"
btc_ohlcv = gemini.fetch_ohlcv(ticker,timeframe='1d')
k = 0.68

def get_target_price(ticker):
  df = pd.DataFrame(btc_ohlcv, columns=['date','open','high','low','close','volume'])
  df['date'] = pd.to_datetime(df['date'], unit='ms')   
  df.set_index('date',inplace=True)
  
  yesterday = df.iloc[-2]

  today_open = yesterday['close']
  yesterday_high = yesterday['high']
  yesterday_low = yesterday['low']
  target = today_open + (yesterday_high - yesterday_low) * k
  return target

now = datetime.datetime.now()
mid = datetime.datetime(now.year,now.month,now.day)
target_price = get_target_price(ticker)


df = pd.DataFrame(btc_ohlcv, columns=['date','open','high','low','close','volume'])
df['date'] = pd.to_datetime(df['date'], unit='ms')    
df.set_index('date',inplace=True)

yesterday = df.iloc[-2]

today_open = yesterday['close']
yesterday_high = yesterday['high']
yesterday_low = yesterday['low']
target_price = today_open + (yesterday_high - yesterday_low) * k

 

print("yesterday high  :", yesterday_high)
print("yesterday low   :", yesterday_low)
print("today open      :", today_open)
print("delta           :", target_price - today_open)
print("target price    :", target_price)


while True:
    try:
        now = datetime.datetime.now()
        if mid < now < mid + datetime.timedelta(seconds=10):
            target_price = get_target_price(ticker)
            mid = datetime.datetime(now.year,now.month,now.day)
            balance = r.get_balance()
            dfb = pd.DataFrame(balance,columns=['type','exchange','currency','amount','available'])
            mybalanceusd = float(dfb.loc[dfb['currency']=='USD','available'])
            mybalancebtc = float(dfb.loc[dfb['currency']=='BTC','available'])
            orderbook = r.get_current_order_book("BTCUSD")
            sell_price = orderbook['bids'][0]['price']
            unit = mybalancebtc
            r.new_order("BTCUSD",unit,sell_price,"sell",["immediate-or-cancel"])

        current_price = r.get_ticker("BTCUSD")
        current_price = current_price['last']
      
      # For selling at a given price
      # if float(current_price) >  specific_selling_price:
      #       balance = r.get_balance()
      #       dfb = pd.DataFrame(balance,columns=['type','exchange','currency','amount','available'])
      #       mybalanceusd = float(dfb.loc[dfb['currency']=='USD','available'])
      #       mybalancebtc = float(dfb.loc[dfb['currency']=='BTC','available'])
      #       orderbook = r.get_current_order_book("BTCUSD")
      #       sell_price = orderbook['bids'][0]['price']
      #       unit = str(mybalancebtc)
      #       r.new_order("BTCUSD",unit,sell_price,"sell",["immediate-or-cancel"])            
      
        if float(current_price) > target_price:
            balance = r.get_balance()
            dfb = pd.DataFrame(balance,columns=['type','exchange','currency','amount','available'])
            mybalanceusd = float(dfb.loc[dfb['currency']=='USD','available'])
            mybalancebtc = float(dfb.loc[dfb['currency']=='BTC','available'])
            orderbook = r.get_current_order_book("BTCUSD")
            buy_price = orderbook['asks'][0]['price']
            unit = mybalanceusd / float(buy_price)
            unit = round(unit,5)-0.00001
            unit = str(unit)
            r.new_order("BTCUSD",unit,buy_price,"buy",["immediate-or-cancel"])

    except:
        print("Error")
    time.sleep(1)