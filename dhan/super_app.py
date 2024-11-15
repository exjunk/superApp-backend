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
import graph_plot as graph_plot
from logger import logger
import risk_manager

dhan = dhanhq("client_id",client_token)
risk_manager.initialize_risk_manager(dhan, client_id)
price_map = {}
timestamps,prices = graph_plot.init_plot()

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
    kill_switch_rules = db_management.get_kill_switch_rules(client_id=client_id)
    index_rules = db_management.get_index_rules(client_id=client_id,index=index)
    
    return kill_switch_rules,index_rules

def emit_order_placed(socketio, order_id):
    """Emit a Socket.IO event for a placed order."""
    socketio.emit('order_placed', {'message': 'New order placed', 'order_id': order_id})


def placeOrder(index_name,option_type,transaction_type,client_order_id,dhan_client_id,product_type,socket_client_id = None,parent_conn = None,confidence = None):
    
    # if the user is pressing CE / PE directly from UI, 
    # i am converting it to BO order so that Auto SL can be placed for the order 
    if product_type == dhan.INTRA:
        product_type = dhan.BO
    
    
    if not risk_manager.check_risk():
        logger.warning("Order placement halted due to risk management rules.")
        return {}
    
    import strike_selection as strike_selection
    try:
        
        index_config = Index_attributes.get_index_attributes(index_name)
        
        kill_switch_rules,index_rules = fetch_index_details_from_db(client_id=dhan_client_id,index=index_name)
        
        trade_qty = index_config.lotsize
        default_qty = index_config.lotsize
        risk = index_config.index_risk
        profit = index_config.profit
        exchange = index_config.exchange_segment
        trading_lot = 1
        index_allowed_to_trade = 0

        if  len (index_rules) > 0:
            trading_lot = index_rules[0]['trading_lot']
            default_qty = index_rules[0]['default_qty']
            trade_qty = int(default_qty) * int(trading_lot)
            risk = index_rules[0]['stop_loss']
            profit = index_rules[0]['profit']
            exchange = index_rules[0]['exchange']
            index_allowed_to_trade = index_rules[0]['trading_enabled']
        
        if index_allowed_to_trade != 1 :
            logger.info(f"{index_name} is not allowed to trade")
            return {}
            
        if confidence != None:
            import math
            
            if confidence == 0.25 :
                profit = risk
                trade_qty = default_qty * math.ceil(trading_lot/4)
            
            if confidence == 0.5 :
                trade_qty = default_qty * math.ceil(trading_lot/2)     

            if confidence == 0.75 :
                profit = float(profit) * float(1.5) 
             
            if confidence == 1 :
                profit = float(profit) * float(2.5)
                   
        multiplier = index_config.multiplier
        current_price = index_config.current_price
        
        strike_price = strike_selection.calculate_trading_strike(DefaultExpiry.current,index_name,current_price,multiplier,option_type)
        correlation_id = client_order_id #utils.generate_correlation_id(max_length=15)
        
        security_id = str(strike_price['SM_SCRIP_CODE'])
        strike_symbol = strike_price['SM_CUSTOM_SYMBOL']
        
        #logger.info(f"security_id --> {security_id}")
        #logger.info(price_map)

        price_diff = 0.0
        if index_name == Index.BANKNIFTY.name:
            price_diff = 7.5
        if index_name == Index.NIFTY.name:
            price_diff = 3.5
        if index_name == Index.FINNIFTY.name:
            price_diff = 4.5
        if index_name == Index.SENSEX.name:
            price_diff = 12.0
            
        current_price = float(price_map[security_id]) - price_diff
        order_type = dhan.MARKET
        
        place_order_result = {}
        logger.info(f"current_price {current_price} -- > order_type {order_type} --> product_type {product_type} --> profit => {profit} --> quantity => {trade_qty}")
        if current_price != None:
            if product_type == dhan.BO:
                order_type = dhan.LIMIT
                
                place_order_result =  dhan.place_order(security_id=security_id,   
                exchange_segment=exchange,
                transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
                quantity=trade_qty,
                product_type=product_type,
                order_type=order_type,
                tag=correlation_id,
                bo_profit_value=str(profit),
                bo_stop_loss_Value=str(risk),
                price=str(current_price))
            
            elif product_type == dhan.INTRA:    
                order_type = dhan.MARKET
                
                place_order_result =  dhan.place_order(security_id=security_id,   
                exchange_segment=exchange,
                transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
                quantity=trade_qty,
                order_type=order_type,
                product_type=product_type,
                tag=correlation_id,
                price=0)
            
            elif product_type == dhan.CO:  
                trigger_price = current_price - float(risk) # SL trigger price 
                order_type = dhan.MARKET
                
                place_order_result =  dhan.place_order(security_id=security_id,   
                exchange_segment=exchange,
                transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
                quantity=trade_qty,
                product_type=product_type,
                order_type=order_type,
                trigger_price=trigger_price,
                price=0,
                tag=correlation_id)
            
            # to handle sensex order manually , no such product_type == sensex exist 
            elif product_type == Index.SENSEX.name: 
                trigger_price = current_price - float(risk) # SL trigger price 
                order_type = dhan.LIMIT
                
                place_order_result =  dhan.place_order(security_id=security_id,   
                exchange_segment=exchange,
                transaction_type= transaction_type, # BUY = dhan.Buy / SELL = dhan.SELL
                quantity=trade_qty,
                product_type=dhan.INTRA,
                order_type=order_type,
                trigger_price=trigger_price,
                price=current_price,
                tag=correlation_id)
               
           
            
            insert_dict = {
                'dhanClientId' : client_id,
                'correlationId':correlation_id,
                'security_id':security_id,
                'exchange_segment':exchange,
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
        logger.info(e)
        return {}

def get_open_positions():
    try:
        return dhan.get_positions()
    except Exception as e:
        return {}

def get_all_open_orders():
    try:
        return dhan.get_order_list()
    except Exception as e:
        return {}



def risk_management():
    fund_limit = dhan.get_fund_limits()
    kill_switch_limits = db_management.get_kill_switch_rules()
    half_hr_limit = kill_switch_limits['half_hour']
    hr_limit = kill_switch_limits['hour']
    kill_switch = kill_switch_limits['kill_switch']
    if 'data' in fund_limit:
        start_day_limit = fund_limit['data']['sodLimit']
        available_balance = fund_limit['data']['availabelBalance']
        
        if available_balance < start_day_limit:
            loss = start_day_limit - available_balance
            loss_percent = (loss/start_day_limit)* 100
            if loss_percent > half_hr_limit and loss_percent < hr_limit :
                pass 
                

        
        

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

def get_open_orders():
    try:
        order_list = dhan.get_order_list()
        if "data" in order_list:
            pending_orders = [order for order in order_list["data"] if order["orderStatus"] == "PENDING"]
            #logger.info(pending_orders)
            return pending_orders
        else:
            return {}
        
    except Exception as e:
        logger.info(e)
        return {}
    
        
def cancel_open_order(order_id):
    try:
        result = dhan.cancel_order(order_id=order_id)
        return result
        
    except Exception as e:
        logger.info(e)
        return {}
    
    
def modify_open_order(order_id,quantity,price,order_type,leg_name,disclosed_qty,trigger_price,validity):
    try:
        result = dhan.modify_order(order_id=order_id,quantity=quantity,price=price,leg_name=leg_name,disclosed_quantity=disclosed_qty,order_type=order_type,trigger_price=trigger_price,validity=validity)
        return result
        
    except Exception as e:
        logger.info(e)
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
        logger.info(strikes)
        return strikes
    except Exception as e:
        return []

def add_trade_level(id,index_name,option_type,price_level,dhan_client_id,confidence):
    logger.info("add_trade_level")
    last_row = db_management.add_trade_trigger_levels(id=id,index_name=index_name,option_type=option_type,level=price_level,dhanClientId=dhan_client_id,confidence=confidence)
    logger.info("db_management")
    get_trade_price_levels()
    logger.info("get_trade_price_levels")
    return last_row

def get_trade_levels(dhan_client_id):
    return db_management.get_trade_trigger_levels(dhan_client_id)

def delete_trade_levels(dhan_client_id,index_name,level):
    db_management.delete_trade_trigger_levels_with_index(client_id=dhan_client_id,index_name=index_name,level=level)
    get_trade_price_levels()

def get_trade_price_levels():
    levels = db_management.get_trade_trigger_levels(client_id=client_id)
    global index_trigger_bnf,index_trigger_finnifty,index_trigger_nifty,index_trigger_sensex

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

    logger.info(index_trigger_bnf)
    logger.info(index_trigger_finnifty)
    logger.info(index_trigger_sensex)
    logger.info(index_trigger_nifty)


get_trade_price_levels()


def get_index_rules(dhan_client_id):
    return db_management.get_index_details(client_id=dhan_client_id)
    
def get_kill_switch_rule(dhan_client_id):
    return db_management.get_kill_switch_rules(client_id=dhan_client_id)

def market_feed_callback(data):
    
    if data['security_id'] == 25 :
        #logger.info(data)
        #ltt = 'LTT' in data
        exist = 'LTP' in data
        if(exist):
            #if ltt:
                #graph_data = f"{data['LTP']},{data['LTT']}"
                #graph_plot.update_plot(graph_data,timestamps=timestamps,prices=prices)
            price = data.get('LTP')
            price_map[Index.BANKNIFTY.name] = price
            level_trigger_logic(index_name=Index.BANKNIFTY.name,price=price,diff_CE=-5,diff_PE=5,index_trigger=index_trigger_bnf)
                    
    if data['security_id'] == 13 :
        #logger.info(data)
        exist = 'LTP' in data
        if(exist):
            price = data.get('LTP')
            price_map[Index.NIFTY.name] = price
            level_trigger_logic(index_name=Index.NIFTY.name,price=price,diff_CE=-2,diff_PE=2,index_trigger=index_trigger_nifty)
           
    if data['security_id'] == 27 :
       exist = 'LTP' in data
       if(exist):
            price = data.get('LTP')
            price_map[Index.FINNIFTY.name] = price
            level_trigger_logic(index_name=Index.FINNIFTY.name,price=price,diff_CE=-3,diff_PE=3,index_trigger=index_trigger_finnifty)
        
    if data['security_id'] == 51 :
        exist = 'LTP' in data
        if(exist):
            price = data.get('LTP')
            price_map[Index.SENSEX.name] = price
            level_trigger_logic(index_name=Index.SENSEX.name,price=price,diff_CE=-5,diff_PE=5,index_trigger=index_trigger_sensex)
        

    elif data['security_id'] != None:
        security_id = data['security_id']
        exist = 'LTP' in data
        if(exist):
            price_map[f"{security_id}"] = data.get('LTP')
       

def level_trigger_logic(price,index_name,diff_CE,diff_PE,index_trigger):
    tempItem = set(index_trigger[0])
    tempItem2 = set(index_trigger[1])
    
    if index_name == Index.SENSEX.name:
        product_type = Index.SENSEX.name
    else:
        product_type = dhan.BO
    
    for item in tempItem:
        diff = float(price) - item
        #logger.printLogs(f"index_name = {index_name} --> diff CE --> {diff} item --> {item} item in --> {item in index_trigger_bnf[0]}")
        if (diff <= 0 and diff >= diff_CE) and (item in index_trigger[0]) :
        
            level_detail = db_management.get_level_details(client_id=client_id,level = utils.format_number(item),index_name=index_name,option_type=Option_Type.CE.name)               
            confidence = level_detail[0]['trade_confidence']
            
            logger.info(f"index_name CE = {index_name} --> diff --> {diff} --> confidence --> {confidence}")
            
            placeOrder(index_name=index_name,option_type=Option_Type.CE.name,transaction_type=dhan.BUY,client_order_id=utils.generate_correlation_id(),dhan_client_id=client_id,product_type=product_type,confidence=confidence)
            index_trigger[0].discard(item)
            db_management.delete_trade_trigger_levels_with_index(client_id=client_id,index_name=index_name,level=item)

    for item in tempItem2:
        diff = float(price) - item
       # logger.printLogs(f"index_name = {index_name} --> diff PE --> {diff} item --> {item} item in --> {item in index_trigger_bnf[1]}")                 
        if (diff >= 0 and diff <= diff_PE) and (item in index_trigger[1]) :
           
            level_detail = db_management.get_level_details(client_id=client_id,level = utils.format_number(item),index_name=index_name,option_type=Option_Type.PE.name)               
            confidence = level_detail[0]['trade_confidence']
               
            logger.info(f"index_name PE = {index_name} --> diff --> {diff} --> confidence --> {confidence}")
            placeOrder(index_name=index_name,option_type=Option_Type.PE.name,transaction_type=dhan.BUY,client_order_id=utils.generate_correlation_id(),dhan_client_id=client_id,product_type=product_type,confidence=None)
            index_trigger[1].discard(item)
            db_management.delete_trade_trigger_levels_with_index(client_id=client_id,index_name=index_name,level=item)
                 


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
             
