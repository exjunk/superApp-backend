from dhanhq import dhanhq

from config import client_token,DefaultExpiry,security_scrip_download_url,client_id
import dhan_socket_connection as dhan_socket
from Enums import Index,Option_Type
from Index_config import Index_config
import utils as utils
import file_downloader as file_downloader
import db_management as db_management
import json
import logger

dhan = dhanhq("client_id",client_token)
price_map = {}

def init():
    file_downloader.manage_file_download(url=security_scrip_download_url,file_path="security.csv")
    

def run_dhan_feed(conn):
    strikes = get_intraday_data()

    feed = dhan_socket.get_dhan_feed(connection=conn,strikes= strikes)
    feed.run_forever()
# init()

def get_order_status(order_id):
    try:
        return dhan.get_order_by_id(order_id=order_id)
    
    except Exception as e:
        return {}

def fetch_index_details_from_db(client_id,index):
    user_config = db_management.get_config_details(client_id=client_id)
    index_risk = db_management.get_index_details(client_id=client_id,index= index)
    
    return user_config,index_risk


def placeOrder(index_name,option_type,transaction_type,client_order_id,dhan_client_id,socket_client_id = None,parent_conn = None):
    import strike_selection as strike_selection
    try:

        index_attribute = Index_attributes.get_index_attributes(index_name)
        user_config,index_risk = fetch_index_details_from_db(client_id=dhan_client_id,index=index_name)
        
        trade_qty = index_attribute.lotsize
        risk = index_attribute.index_risk
        profit = index_attribute.profit

        if len(user_config) > 0 and len (index_risk) > 0:
            trade_qty = index_risk[0]['max_qty']
            risk = index_risk[0]['stop_loss']
            profit = index_risk[0]['profit']



        multiplier = index_attribute.multiplier
        current_price = index_attribute.current_price
        
        strike_price = strike_selection.calculate_trading_strike(DefaultExpiry.current,index_name,current_price,multiplier,option_type)
        correlation_id = client_order_id #utils.generate_correlation_id(max_length=15)
        order_type = dhan.MARKET
        security_id = str(strike_price['SEM_SMST_SECURITY_ID'])
        strike_symbol = strike_price['SEM_CUSTOM_SYMBOL']
        product_type = dhan.BO #dhan.INTRA for intraday - bracket order so that I can add take profit and Stop Loss
        
        place_order_result =  dhan.place_order(security_id=security_id,   
        exchange_segment=index_attribute.exchange_segment,
        transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
        quantity=trade_qty,
        order_type=order_type,
        product_type=product_type,
        tag=correlation_id,
        bo_profit_value=str(profit),
        bo_stop_loss_Value=str(risk),
        price=0)

        # msg = {}
        # msg['topic'] = 'sub'
        # msg['security_id'] = security_id
        # msg['symbol'] = strike_symbol
        # msg['index'] = index_attribute.name

        # parent_conn.send(msg)

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
        
        api_status = place_order_result.get('status')
        place_order_result['security_id'] = security_id
        if(api_status == 'success' and order_type == dhan.MARKET):
            id = place_order_result['data']['orderId']
            order_status = place_order_result['data']['orderStatus']

            # if(order_status == enum.Order_status.PENDING.name or order_status == enum.Order_status.TRANSIT.name):
            #     checker = StatusChecker(timeout=10,dhan=dhan,order_id=id,correlation_id=correlation_id,security_id=security_id,socket_client_id=socket_client_id)
            #     checker.start()
    	
        #dhan_socket.subscribe_symbols(feed,security_id)
        return place_order_result
    
    except Exception as e:
        return {}


def get_open_positions():
    try:
        return dhan.get_positions()
    except Exception as e:
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
        return {}
    

def getOrders():
    try:
        return dhan.get_order_list()
    
    except Exception as e:
        return {}
    
        
def getFundLimit():
    try:
        return dhan.get_fund_limits()
    except Exception as e:
        return {}

def get_intraday_data():
    try:
        list = [{'security_id' : '25','exchange_segment' : 'IDX_I','instrument_type' : 'INDEX'},
                {'security_id' : '13','exchange_segment' : 'IDX_I','instrument_type' : 'INDEX'},
                {'security_id' : '51','exchange_segment' : 'IDX_I','instrument_type' : 'INDEX'},
                {'security_id' : '27','exchange_segment' : 'IDX_I','instrument_type' : 'INDEX'}]
        result = []

        for item in list:
            response = dhan.intraday_minute_data(security_id=item['security_id'],exchange_segment=item['exchange_segment'],instrument_type=item['instrument_type'])
            result.append({'security_id' : item['security_id'] , 'close' : response['data']['close'][-1]})

        import strike_selection as strike_selection    
        #for item in result:
        strikes = []
        strikes.append({'index' : Index.BANKNIFTY.name ,'value': strike_selection.calculate_near_strikes(current_price=result[0]['close'],index_name=Index.BANKNIFTY.name,index_multiplier=100)})  
        strikes.append({'index' : Index.NIFTY.name ,'value': strike_selection.calculate_near_strikes(current_price=result[1]['close'],index_name=Index.NIFTY.name,index_multiplier=50)} )
        strikes.append({'index' : Index.SENSEX.name,'value' :strike_selection.calculate_near_strikes(current_price=result[2]['close'],index_name=Index.SENSEX.name,index_multiplier=100)})  
        strikes.append({'index' : Index.FINNIFTY.name,'value' :strike_selection.calculate_near_strikes(current_price=result[3]['close'],index_name=Index.FINNIFTY.name,index_multiplier=50)} )
        
        return strikes
    except Exception as e:
        return []


def get_trade_price_levels():
    levels = db_management.get_trade_trigger_levels(client_id=client_id)
    global index_trigger_bnf,index_trigger_finnifty,index_trigger_finnifty,index_trigger_sensex

    index_trigger_bnf = [set(),set()]
    index_trigger_nifty = [set(),set()]
    index_trigger_finnifty = [set(),set()]
    index_trigger_sensex = [set(),set()]
    for item in levels:
        if(item['index_name'] == Index.BANKNIFTY.name):
            if(item['option_type'] == Option_Type.CE.name):
                index_trigger_bnf[0].add(item['price_level']) 
            if(item['option_type'] == Option_Type.PE.name):
                index_trigger_bnf[1].add(item['price_level']) 
        
        if(item['index_name'] == Index.NIFTY.name):
            if(item['option_type'] == Option_Type.CE.name):
                index_trigger_nifty[0].add(item['price_level']) 
            if(item['option_type'] == Option_Type.PE.name):
                index_trigger_nifty[1].add(item['price_level']) 

        if(item['index_name'] == Index.SENSEX.name):
            if(item['option_type'] == Option_Type.CE.name):
                index_trigger_sensex[0].add(item['price_level']) 
            if(item['option_type'] == Option_Type.PE.name):
                index_trigger_sensex[1].add(item['price_level'])  

        if(item['index_name'] == Index.FINNIFTY.name):
            if(item['option_type'] == Option_Type.CE.name):
                index_trigger_finnifty[0].add(item['price_level']) 
            if(item['option_type'] == Option_Type.PE.name):
                index_trigger_finnifty[1].add(item['price_level']) 

    logger.printLogs(index_trigger_bnf)
    logger.printLogs(index_trigger_finnifty)
    logger.printLogs(index_trigger_sensex)
    logger.printLogs(index_trigger_nifty)


get_trade_price_levels()

def market_feed_callback(data):
    if data['security_id'] == 25 :
        exist = 'LTP' in data
        if(exist):
            price = data.get('LTP')
            price_map[Index.BANKNIFTY.name] = price
            
            for item in index_trigger_bnf[0]:
                diff = float(price) - item
                if diff <= 0 and diff >= -5:
                    placeOrder(index_name=Index.BANKNIFTY.name,option_type=Option_Type.CE.name,transaction_type=dhan.BUY,client_order_id=utils.generate_correlation_id(),dhan_client_id=client_id) 
            

    if data['security_id'] == 13 :
        exist = 'LTP' in data
        if(exist):
            price_map[Index.NIFTY.name] = data.get('LTP')
    if data['security_id'] == 27 :
       exist = 'LTP' in data
       if(exist):
            price_map[Index.FINNIFTY.name] = data.get('LTP')
    if data['security_id'] == 51 :
        exist = 'LTP' in data
        if(exist):
            price_map[Index.SENSEX.name] = data.get('LTP')
       
        

class Index_attributes:
        def get_index_attributes(name)->(Index_config):
             if(name == Index.BANKNIFTY.name): 
                 return Index_config(name,100,15,20,25,'NSE_FNO',price_map[name])
             if(name == Index.SENSEX.name): 
                return Index_config(name,100,10,25,30,'BSE_FNO',price_map[name])
             if(name == Index.NIFTY.name): 
                return Index_config(name,50,25,5,8,'NSE_FNO',price_map[name])
             if(name == Index.FINNIFTY.name): 
                return Index_config(name,50,40,6,10,'NSE_FNO',price_map[name])
             
