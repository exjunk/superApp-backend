from dhanhq import dhanhq
import strike_selection as strike_selection
from config import client_token,DefaultExpiry
import dhan_socket_connection as dhan_socket
import client_socket_connection as client_socket
from Enums import Index
from Index_config import Index_config
from config import client_token
import wget


dhan = dhanhq("client_id",client_token)
feed = dhan_socket.getFeed()
dhan_socket.runSocketThread(feed=feed) #Socket connection dhan IQ

client_socket.run_server()

#def close_socket():
 #   incoming_socket.close_socket(my_socket,connection)


def download_security_csv():
    wget.download("https://images.dhan.co/api-data/api-scrip-master.csv","security.csv")
#download_security_csv()
#def initStrikePrice():
   #strike_selection.download_security_csv()
   #strike_selection.calculate_trading_strike(True,"NIFTY",22300,50)
   #strike_selection.calculate_trading_strike(True,"BANKNIFTY",48285,100)
   #strike_selection.calculate_trading_strike(True,"FINNIFTY",21543,50)
   #strike_selection.calculate_trading_strike(True,"SENSEX",73511,100)
   

def placeOrder(index_name,option_type,transaction_type):
    index_attribute = Index_attributes.get_index_attributes(index_name)
    
    multiplier = index_attribute.multiplier
    current_price = index_attribute.current_price
    strike_price = strike_selection.calculate_trading_strike(DefaultExpiry.current,index_name,current_price,multiplier,option_type)
    
    return dhan.place_order(security_id=str(strike_price['SEM_SMST_SECURITY_ID']),   
    exchange_segment=index_attribute.exchange_segment,
    transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
    quantity=index_attribute.lotsize,
    order_type=dhan.MARKET,
    product_type=dhan.INTRA,
    price=0)

def get_open_positions():
    return dhan.get_positions()

def get_order_status(order_id):
    return dhan.get_order_by_id(order_id=order_id)

def closeAllPositions(security_id,exchange_segment,transaction_type,quantity,product_type):
    return dhan.place_order(security_id=security_id,   
        exchange_segment=exchange_segment,
        transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
        quantity=quantity,
        order_type=dhan.MARKET,
        product_type= product_type,#dhan.INTRA,
        price=0)
    

def getOrders():
   return dhan.get_order_list()

def getFundLimit():
    return dhan.get_fund_limits()

class Index_attributes:
        def get_index_attributes(name)->(Index_config):
             if(name == Index.BANKNIFTY.name): 
                 return Index_config(name,100,15,'NSE_FNO',dhan_socket.bankNifty_current_price)
             if(name == Index.SENSEX.name): 
                return Index_config(name,100,10,'BSE_FNO',dhan_socket.sensex_current_price)
             if(name == Index.NIFTY.name): 
                return Index_config(name,50,25,'NSE_FNO',dhan_socket.nifty_current_price)
             if(name == Index.FINNIFTY.name): 
                return Index_config(name,50,40,'NSE_FNO',dhan_socket.finnifty_current_price)
