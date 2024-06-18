from dhanhq import dhanhq

from config import client_token,DefaultExpiry,security_scrip_download_url,client_id
import dhan_socket_connection as dhan_socket
from Enums import Index
from Index_config import Index_config
import utils as utils
import file_downloader as file_downloader
import db_management as db_management
import json

dhan = dhanhq("client_id",client_token)

def init():
    file_downloader.manage_file_download(url=security_scrip_download_url,file_path="security.csv")
    

def run_dhan_feed():
    feed = dhan_socket.get_dhan_feed()
    feed.run_forever()
# init()

def get_order_status(order_id):
    try:
        return dhan.get_order_by_id(order_id=order_id)
    
    except Exception as e:
        print(e)
        return {}
   

def placeOrder(index_name,option_type,transaction_type,client_order_id,socket_client_id):
    import strike_selection as strike_selection

    try:
        index_attribute = Index_attributes.get_index_attributes(index_name)
        multiplier = index_attribute.multiplier
        current_price = index_attribute.current_price
        
        strike_price = strike_selection.calculate_trading_strike(DefaultExpiry.current,index_name,current_price,multiplier,option_type)
        correlation_id = client_order_id #utils.generate_correlation_id(max_length=15)
        order_type = dhan.MARKET
        security_id = str(strike_price['SEM_SMST_SECURITY_ID'])
        strike_symbol = strike_price['SEM_CUSTOM_SYMBOL']
        product_type = dhan.INTRA

        place_order_result =  dhan.place_order(security_id=security_id,   
        exchange_segment=index_attribute.exchange_segment,
        transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
        quantity=index_attribute.lotsize,
        order_type=order_type,
        product_type=product_type,
        tag=correlation_id,
        price=0)

        insert_dict = {
            'dhanClientId' : client_id,
            'correlationId':correlation_id,
            'security_id':security_id,
            'exchange_segment':index_attribute.exchange_segment,
            'order_type':order_type,
            'transaction_type':transaction_type,
            'product_type':product_type,
            'trading_symbol':strike_symbol,
            'orderId':''
        }
        data = json.dumps(insert_dict)

        db_management.insert_order(data=data,table_name='order_placement_client')
        


        print(place_order_result)
        api_status = place_order_result.get('status')
        if(api_status == 'success' and order_type == dhan.MARKET):
            id = place_order_result['data']['orderId']
            order_status = place_order_result['data']['orderStatus']

            # if(order_status == enum.Order_status.PENDING.name or order_status == enum.Order_status.TRANSIT.name):
            #     checker = StatusChecker(timeout=10,dhan=dhan,order_id=id,correlation_id=correlation_id,security_id=security_id,socket_client_id=socket_client_id)
            #     checker.start()
    	
        #dhan_socket.subscribe_symbols(feed,security_id)
        return place_order_result
    
    except Exception as e:
        print(e)
        return {}


def get_open_positions():
    try:
        return dhan.get_positions()
    except Exception as e:
        print(e)
        return {}



def closeAllPositions(security_id,exchange_segment,transaction_type,quantity,product_type):
    try:
        correlation_id = utils.generate_correlation_id(max_length=15)
        return dhan.place_order(security_id=security_id,   
            exchange_segment=exchange_segment,
            transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
            quantity=quantity,
            order_type=dhan.MARKET,
            product_type= product_type,#dhan.INTRA,
            tag=correlation_id,
            price=0)
    except Exception as e:
        print(e)
        return {}
    

def getOrders():
    try:
        return dhan.get_order_list()
    
    except Exception as e:
        print(e)
        return {}
    
        
def getFundLimit():
    try:
        return dhan.get_fund_limits()
    except Exception as e:
        print(e)
        return {}
   
        
    

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
