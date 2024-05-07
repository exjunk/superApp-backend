from dhanhq import dhanhq
import wget
import pandas as pd
import numpy as np
import strike_selection as strike_selection

from Enums import Index

#dhan = dhanhq("client_id","eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzE2NzU3NTI5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDMyMzU2OSJ9.vFZDPb5I7BOHnKfg88lw8DvRUuXxO0Lc2JAbs7cuyXX5BKA-9fgBns8Zo2iwdO2jfi0f8-4ocNdlfX9O-Kq7-Q")

    

def initStrikePrice():
   #strike_selection.download_security_csv()
   strike_selection.calculate_trading_strike(True,"NIFTY",22300,50)
   strike_selection.calculate_trading_strike(True,"BANKNIFTY",48285,100)
   strike_selection.calculate_trading_strike(True,"FINNIFTY",21543,50)
   strike_selection.calculate_trading_strike(True,"SENSEX",73511,100)
   
initStrikePrice()

def placeOrder():
    return dhan.place_order(security_id='1333',   #hdfcbank
    exchange_segment=dhan.NSE,
    transaction_type=dhan.BUY,
    quantity=100,
    order_type=dhan.MARKET,
    product_type=dhan.MTF,
    price=0)

def getOrders():
   return dhan.get_order_list()

def downloadSecurityScrip():
   wget.download("https://images.dhan.co/api-data/api-scrip-master.csv","security.csv")

def fetchDetailsFromCSV():
   data = pd.read_csv('security.csv')
   df = pd.DataFrame(data)
   print(df["OPTIDX"])