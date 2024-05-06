from dhanhq import dhanhq
import wget
import pandas as pd
import numpy as np
from datetime import datetime

#dhan = dhanhq("client_id","eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzE2NzU3NTI5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDMyMzU2OSJ9.vFZDPb5I7BOHnKfg88lw8DvRUuXxO0Lc2JAbs7cuyXX5BKA-9fgBns8Zo2iwdO2jfi0f8-4ocNdlfX9O-Kq7-Q")
#wget.download("https://images.dhan.co/api-data/api-scrip-master.csv","security.csv")

data = pd.read_csv('security.csv',encoding='utf-8', engine='python')
df = pd.DataFrame(data)
df.replace(r'^\s*$', np.nan, regex=True)
filterOPT = df[df['SEM_INSTRUMENT_NAME'] == 'OPTIDX']
dfOPT = pd.DataFrame(filterOPT)
filterBNF = dfOPT[(dfOPT["SEM_TRADING_SYMBOL"].str.contains("BANKNIFTY"))]

today = datetime.today()

def calculateDifference(date_str):
    # Convert the string to datetime object with format specified
  date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
  # Calculate difference in days
  days_diff = (date_obj - today).days
  # Calculate difference in hours (optional)
  hours_diff = (date_obj - today).seconds // 3600  # Assuming difference is less than a day
  return pd.Series({'diff_Days': days_diff, 'diff_Hours': hours_diff})  # Create a Series

# Apply the function to the 'date' column and add as a new row
df_diff = filterBNF.apply(lambda row: calculateDifference(row['SEM_EXPIRY_DATE']), axis=1)
filterBNF = pd.concat([filterBNF, df_diff], axis=1)
filterBNF.sort_values(by='diff_Days')





#filterBNF = df[df['SEM_TRADING_SYMBOL'].str.contains('BANKNIFTY')]
print(filterBNF.head)

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