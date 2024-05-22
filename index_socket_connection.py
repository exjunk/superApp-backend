from dhanhq import marketfeed
from config import client_token,client_id
import threading


# Add your Dhan Client ID and Access Token
access_token = client_token

bankNifty_current_price = 0
finnifty_current_price = 0
sensex_current_price = 0
nifty_current_price = 0
symbol_sub = {}

# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 

instruments = [(0, "25"),(0,"13"),(0,"51"),(0,"27")]  #13 - Nifty , 25 BNF , 27 Finnifty , 51 Sensex 
                                            # exchange segment - 0 for INDEX , 1 for EQUITY

# Type of data subscription
subscription_code = marketfeed.Ticker

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth
async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    global bankNifty_current_price
    global finnifty_current_price 
    global sensex_current_price
    global nifty_current_price
    global symbol_sub
    print("Received:", message)
  # ticker_data = Ticker_data(**json.loads(str(message)))
    if(message['security_id'] == 25):
     exist = 'LTP' in message
     if(exist):
        bankNifty_current_price = message.get('LTP')
    
    elif(message['security_id'] == 27):
     exist = 'LTP' in message
     if(exist):
        finnifty_current_price = message.get('LTP')

    elif(message['security_id'] == 13):
     exist = 'LTP' in message
     if(exist):
        nifty_current_price = message.get('LTP')

    elif(message['security_id'] == 51):
     exist = 'LTP' in message
     if(exist):
        sensex_current_price = message.get('LTP')
    
    else:
       exist = 'LTP' in message
       if(exist):
        symbol_sub = dict(message['security_id'],message.get('LTP'))

    
    

print("Subscription code :"+str(subscription_code))

def getFeed():
    return marketfeed.DhanFeed(client_id,access_token,instruments,subscription_code,on_connect=on_connect,
        on_message=on_message)
    
def runSocketThread(feed):    
    def run_from_thread():
        feed.run_forever()

    thread = threading.Thread(target=run_from_thread)
    thread.start()

def subScribeSymbols(feed,security_id):
       feed.subscribe_symbols(subscription_code,security_id)   
       

def unsubScribeSymbols(feed,security_id):
       feed.unsubscribe_symbols(subscription_code,security_id)
       symbol_sub.pop(security_id,None)     

