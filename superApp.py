from dhanhq import dhanhq
import strike_selection as strike_selection
from config import DefaultExpiry
from socket_connection import BankNifty_current_price

client_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzE2NzU3NTI5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDMyMzU2OSJ9.vFZDPb5I7BOHnKfg88lw8DvRUuXxO0Lc2JAbs7cuyXX5BKA-9fgBns8Zo2iwdO2jfi0f8-4ocNdlfX9O-Kq7-Q"

dhan = dhanhq("client_id",client_token)
#strike_selection.find_index_list()
#def initStrikePrice():
   #strike_selection.download_security_csv()
   #strike_selection.calculate_trading_strike(True,"NIFTY",22300,50)
   #strike_selection.calculate_trading_strike(True,"BANKNIFTY",48285,100)
   #strike_selection.calculate_trading_strike(True,"FINNIFTY",21543,50)
   #strike_selection.calculate_trading_strike(True,"SENSEX",73511,100)
   

def placeOrder(index_name,option_type):
    strike_price = strike_selection.calculate_trading_strike(DefaultExpiry.current,index_name,BankNifty_current_price,option_type)
    
    return dhan.place_order(security_id=strike_price['SEM_SMST_SECURITY_ID'],   #hdfcbank
    exchange_segment=dhan.NSE,
    transaction_type=dhan.BUY,
    quantity=100,
    order_type=dhan.MARKET,
    product_type=dhan.INTRA,
    price=0)

def getOrders():
   return dhan.get_order_list()
