import wget
import pandas as pd
import numpy as np
from datetime import datetime
from Enums import Index
import os.path


def find_index_list():
    data = pd.read_csv('security.csv',encoding='utf-8', engine='python')
    df = pd.DataFrame(data)
    index_list = df[df['SEM_INSTRUMENT_NAME'] == 'FUTIDX'] # INDEX , FUTIDX ,OPTIDX , EQUITY
    index_list.to_csv("index_list_fut.csv")

def read_csv():
    #download_security_csv()
    data = pd.read_csv('security.csv',encoding='utf-8', engine='python')
    df = pd.DataFrame(data)
    df.replace(r'^\s*$', np.nan, regex=True)
    filterOPT = df[df['SEM_INSTRUMENT_NAME'] == 'OPTIDX']
    return filterOPT

def calculateDifference(date_str):
  today = datetime.today()
  date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
  days_diff = (date_obj - today).days
  hours_diff = (date_obj - today).seconds // 3600  # Assuming difference is less than a day
  return pd.Series({'diff_Days': days_diff, 'diff_Hours': hours_diff})  # Create a Series

def pre_requisite_strike_selection(filterOPT,index_name):
    filter_index = filterOPT[(filterOPT["SEM_TRADING_SYMBOL"].str.startswith(index_name+'-'))]
    df_diff = filter_index.apply(lambda row: calculateDifference(row['SEM_EXPIRY_DATE']), axis=1)
    filter_index = pd.concat([filter_index, df_diff], axis=1)
    filter_index = filter_index.sort_values(by='diff_Days')
    

    all_unique_index = filter_index['diff_Days'].drop_duplicates().index.tolist()

    first_index = filter_index.loc[all_unique_index[:1]]
    second_index = filter_index.loc[all_unique_index[1:2]]


    # Extract unique values from 'Days' column (including duplicates in those rows)
    first_unique_days = first_index['diff_Days'].unique()
    second_unique_days = second_index['diff_Days'].unique()
    

    # Filter the DataFrame to include rows with top two unique minimum differences
    current_expiry_df = filter_index[filter_index['diff_Days'].isin(first_unique_days)]
    next_expiry_df = filter_index[filter_index['diff_Days'].isin(second_unique_days)]

    current_expiry_df = current_expiry_df.sort_values(by='SEM_STRIKE_PRICE')
    next_expiry_df = next_expiry_df.sort_values(by='SEM_STRIKE_PRICE')

    return current_expiry_df,next_expiry_df


filterOPT = read_csv()
bnf_expiry_current,bnf_expiry_next = pre_requisite_strike_selection(filterOPT,Index.BANKNIFTY.name)
nifty_expiry_current,nifty_expiry_next = pre_requisite_strike_selection(filterOPT,Index.NIFTY.name)
finnifty_expiry_current,fininifty_expiry_next = pre_requisite_strike_selection(filterOPT,Index.FINNIFTY.name)
sensex_expiry_current,sensex_expiry_next = pre_requisite_strike_selection(filterOPT,Index.SENSEX.name)

def calculate_trading_strike(is_current_expiry,index_name,current_price,index_multiplier,option_type)->(pd.DataFrame):
    if(index_name == Index.BANKNIFTY.name):
        current_expiry_df = bnf_expiry_current
        next_expiry_df = bnf_expiry_next

    if(index_name == Index.NIFTY.name):
        current_expiry_df = nifty_expiry_current
        next_expiry_df = nifty_expiry_next

    if(index_name == Index.FINNIFTY.name):
        current_expiry_df = finnifty_expiry_current
        next_expiry_df = fininifty_expiry_next

    if(index_name == Index.SENSEX.name):
        current_expiry_df = sensex_expiry_current
        next_expiry_df = sensex_expiry_next

    print(current_price)

    lower_bound = float(current_price) - (2*index_multiplier)
    upper_bound = float(current_price) + (2*index_multiplier)

    current_expiry_strike_df =  current_expiry_df[current_expiry_df['SEM_STRIKE_PRICE'].between(lower_bound,upper_bound)]
    next_expiry_strike_df = next_expiry_df[next_expiry_df['SEM_STRIKE_PRICE'].between(lower_bound,upper_bound)]

    current_expiry_CE_df = current_expiry_strike_df[current_expiry_strike_df['SEM_OPTION_TYPE'] == 'CE']
    current_expiry_PE_df = current_expiry_strike_df[current_expiry_strike_df['SEM_OPTION_TYPE'] == 'PE']

    next_expiry_CE_df = next_expiry_strike_df[next_expiry_strike_df['SEM_OPTION_TYPE'] == 'CE']
    next_expiry_PE_df = next_expiry_strike_df[next_expiry_strike_df['SEM_OPTION_TYPE'] == 'PE']


    if(is_current_expiry):
        if(len(current_expiry_CE_df) > 0):
            trading_CE = current_expiry_CE_df.iloc[0]
        if(len(current_expiry_PE_df) > 0):
            trading_PE = current_expiry_PE_df.iloc[-1]
    else:
        if(len(next_expiry_CE_df) > 0):
            trading_CE = next_expiry_CE_df.iloc[0]
        if(len(next_expiry_PE_df) > 0):
            trading_PE = next_expiry_PE_df.iloc[-1]

    if(option_type == "PE"):
        return trading_PE
    else:
        return trading_CE




    
        




