from dhanhq import marketfeed
from superApp import client_token
from ticker_data_model import Ticker_data
import json

# Add your Dhan Client ID and Access Token
client_id = "1100323569"
access_token = client_token

BankNifty_current_price = 0

# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 

instruments = [(0, "25"),(0,"13"),(0,"51")]  # 0 = NSE , 1 = BSE

# Type of data subscription
subscription_code = marketfeed.Ticker

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth
async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
   # print("Received:", message)
   ticker_data = Ticker_data(**json.loads(message))
   if(ticker_data.security_id == 25):
       BankNifty_current_price = ticker_data.ltp

print("Subscription code :"+str(subscription_code))

feed = marketfeed.DhanFeed(client_id,access_token,instruments,subscription_code,on_connect=on_connect,
    on_message=on_message)

feed.run_forever()
