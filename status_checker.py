import threading
import time
import Enums as enum
import client_socket_connection as client_socket_connection
import dhan_socket_connection as dhan_socket_connection

class StatusChecker:
    def __init__(self,timeout,dhan,order_id):
        self.timeout = timeout
        self.last_response = None
        self.stop_event = threading.Event()
        self.dhan = dhan
        self.order_id = order_id

    def check_status(self):
        try:
            start_time = time.time()
            while not self.stop_event.is_set():
                response = self.dhan.get_order_by_id(order_id=self.order_id)
                
                status = response['data']['orderStatus']
                if status != enum.Order_status.TRADED.name:
                    current_response = status  # Assuming the response is JSON
                    if self.last_response is not None and current_response == self.last_response:
                        if time.time() - start_time >= self.timeout:
                            self.cancel_request()
                            self.stop_event.set()
                            break
                    else:
                        self.last_response = current_response
                        start_time = time.time()
                else:
                    self.stop_event.set()       
                time.sleep(1)

        except Exception as e :
            print(e)    
            self.stop_event.set()      

                     
    def cancel_request(self):
        try:
            self.dhan.cancel_order(self.order_id)
        except Exception as e :
            print(e)    
            self.stop_event.set()  

    def start(self):
        self.thread = threading.Thread(target=self.check_status)
        self.thread.start()

    #to stop from other part of code 
    def stop(self):
        self.stop_event.set()
        self.thread.join()
        

