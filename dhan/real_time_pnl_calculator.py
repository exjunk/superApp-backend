
import time
import threading
from logger import logger

class RealtimePnLCalculator:
    def __init__(self, dhan, socketio):
        self.dhan = dhan
        self.socketio = socketio
        self.running = False
        self.thread = None

    def calculate_pnl(self):
        try:
            positions = self.dhan.get_positions()
            total_pnl = 0
            realized_pnl = 0
            unrealized_pnl = 0
            
            if 'data' not in positions:
                logger.error("Failed to retrieve positions")
                return None

            for position in positions['data']:
                if position['positionType'] == 'CLOSED':
                    realized_pnl += position['realizedProfit']
                else:
                    unrealized_pnl += position['unrealizedProfit']
                
                # Subtracting a fixed brokerage amount per position
                total_pnl -= 40  # Assuming 40 is the brokerage per position

            total_pnl = realized_pnl + unrealized_pnl

            return {
                'total_pnl': total_pnl,
                'realized_pnl': realized_pnl,
                'unrealized_pnl': unrealized_pnl
            }

        except Exception as e:
            logger.error(f"Error in calculating PnL: {str(e)}")
            return None

    def send_pnl_update(self):
        pnl_data = self.calculate_pnl()
        if pnl_data:
            self.socketio.emit('pnl', pnl_data)

    def run(self):
        while self.running:
            self.send_pnl_update()
            time.sleep(1)  # Wait for 1 second before the next update

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()