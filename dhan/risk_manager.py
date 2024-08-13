# risk_manager.py

import time
from datetime import datetime, timedelta
from config import client_token
from logger import logger
import threading
import utils as utils

class RiskManager:
    def __init__(self, dhan, client_id):
        self.dhan = dhan
        self.client_id = client_id
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        self.resting_until = None
        self.kill_switch_activated = False

    def risk_management(self):
        logger.info("risk management init")
        current_time = datetime.now()

        # Check if we're in a resting period
        if self.resting_until and current_time < self.resting_until:
            return False

        # Check if kill switch is activated
        if self.kill_switch_activated:
            return False

        # Only check every 2 minutes
        if (current_time - self.last_check_time).total_seconds() < 120:
            return True

        self.last_check_time = current_time

        try:
            #logger.info("risk management fund_limit")
            
            positions = self.dhan.get_positions()
            pnl = 0
            
            for position in positions.get('data', []):
                if position['positionType'] == 'CLOSED':
                    pnl = pnl + position['realizedProfit']                     
                else:
                    pnl = pnl + position['unrealizedProfit'] 
                
                pnl = pnl - 40 #brokerage 
                     
            
            fund_limit = self.dhan.get_fund_limits()
            logger.info(f"risk management {fund_limit}")
            if 'data' not in fund_limit:
                logger.error("Failed to retrieve fund limits")
                return False

            data = fund_limit['data']
            sod_limit = data['sodLimit']
           # available_balance = data['availabelBalance']
           # utilized_balance = data['utilizedAmount']
            
            #since pnl is already negative,so we have to add
            #loss = sod_limit + pnl
            loss_percent = (pnl / sod_limit) * 100
            logger.info(f"{pnl} {sod_limit}  {loss_percent}")
            if loss_percent < 0:
                if abs(loss_percent) >= 10:
                    logger.warning(f"Loss percent {loss_percent}% exceeds -10%. Activating kill switch.")
                    self.kill_switch_activated = True
                    self.close_all_positions_and_orders()
                    #self.send_kill_switch_request()
                    return False
                elif abs(loss_percent) >= 7.5 and abs(loss_percent) < 10 :
                    logger.warning(f"Loss percent {loss_percent}% between -7.5% and -10%. Halting orders for 1 hour.")
                    self.resting_until = current_time + timedelta(hours=1)
                    return False
                elif abs(loss_percent) >= 5 and abs(loss_percent) < 7.5:
                    logger.warning(f"Loss percent {loss_percent}% between -5% and -7.5%. Halting orders for 30 minutes.")
                    self.resting_until = current_time + timedelta(minutes=30)
                    return False
                else:
                    return True
            else:
                return True

        except Exception as e:
            logger.error(f"Error in risk management: {str(e)}")
            return False

    def close_all_positions_and_orders(self):
        try:
            # Close all positions
            positions = self.dhan.get_positions()
            for position in positions.get('data', []):
                if position['positionType'] != 'CLOSED' and position['productType'] != self.dhan.CO and position['productType'] != self.dhan.BO :
                    correlation_id = utils.generate_correlation_id(max_length=15)
                    self.dhan.place_order(
                        security_id=position['securityId'],
                        exchange_segment=position['exchangeSegment'],
                        transaction_type=self.dhan.SELL if position['buyQty'] > 0 else self.dhan.BUY,
                        quantity=abs(position['buyQty']),
                        order_type=self.dhan.MARKET,
                        product_type=position['productType'],
                        price=0,
                        tag = correlation_id
                    )
                    
            # Cancel all open orders
            open_orders = self.dhan.get_order_list()
            for order in open_orders.get('data', []):
                if order['orderStatus'] == 'PENDING':
                    self.dhan.cancel_order(order_id=order['orderId'])

            logger.info("All positions closed and open orders cancelled.")
        except Exception as e:
            logger.error(f"Error in closing positions and orders: {str(e)}")

    def send_kill_switch_request(self):
        try:
            import requests

            url = 'https://api.dhan.co/killSwitch'
            params = {'killSwitchStatus': 'ACTIVATE'}
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'access-token': client_token  # Replace 'JWT' with your actual JWT token
            }

            response = requests.post(url, params=params, headers=headers)

            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
        except Exception as e:
            logger.error(f"Error in activating kill switch: {str(e)}")
                  

    def periodic_risk_check(self):
        while True:
            self.risk_management()
            time.sleep(120)  # Sleep for 2 minutes

    def start_periodic_check(self):
        risk_check_thread = threading.Thread(target=self.periodic_risk_check)
        risk_check_thread.daemon = True
        risk_check_thread.start()

# Create a global instance of RiskManager
risk_manager = None

def initialize_risk_manager(dhan, client_id):
    global risk_manager
    risk_manager = RiskManager(dhan, client_id)
    risk_manager.start_periodic_check()

def check_risk():
    global risk_manager
    if risk_manager is None:
        logger.error("RiskManager not initialized")
        return False
    return risk_manager.risk_management()