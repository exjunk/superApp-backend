from dhanhq import marketfeed
from config import client_token,client_id
import threading
import asyncio
from Enums import Index


# Add your Dhan Client ID and Access Token
access_token = client_token

bankNifty_current_price = 0
finnifty_current_price = 0
sensex_current_price = 0
nifty_current_price = 0
symbol_sub = {}

# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 

instruments = [(marketfeed.IDX, "25"),(marketfeed.IDX,"13"),(marketfeed.IDX,"51"),(marketfeed.IDX,"27")]  #13 - Nifty , 25 BNF , 27 Finnifty , 51 Sensex 
                                            # exchange segment - 0 for INDEX , 1 for EQUITY

# Type of data subscription
subscription_code = marketfeed.Ticker


# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth
async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
  #  print("Received:", message)
  # ticker_data = Ticker_data(**json.loads(str(message)))
    conn.send(message)
        


def get_dhan_feed(connection,strikes):
    global conn
    global feed

    i = 0
    for item in strikes:
        
        for CE in item['value']:           
            if item['index'] == Index.SENSEX.name:
                segment = marketfeed.BSE_FNO
            else:
                segment = marketfeed.NSE_FNO

            for call in CE :
                i = i+1
                instruments.append((segment,str(call)))

    feed = marketfeed.DhanFeed(client_id,access_token,instruments,subscription_code,on_connect=on_connect,
        on_message=on_message)
    conn = connection #process pipe connection

    receiver_thread(conn)
    return feed

def receiver_parse_msg(msg):
   if msg['topic'] == 'sub':
      subscribe_symbols(msg['security_id'],msg['index'])

def receiver_thread(conn):
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=receiver, args=(conn,loop,))
    thread.start()
    return thread

def receiver(conn,loop):
   asyncio.set_event_loop(loop)
   while True:
        msg = conn.recv()
        receiver_parse_msg(msg)
        if msg == "STOP":
            break

async def run_feed(feed):
   await feed.run_forever()



def subscribe_symbols(security_id,index):
       if index == Index.SENSEX.name :
           segment = marketfeed.BSE_FNO
       else :
           segment = marketfeed.NSE_FNO

       symbols = [(segment, security_id)]
       feed.subscribe_symbols(symbols) 
       
       

async def unsubscribe_symbols(feed,security_id):
       feed.unsubscribe_symbols(subscription_code,security_id)
       symbol_sub.pop(security_id,None)     

