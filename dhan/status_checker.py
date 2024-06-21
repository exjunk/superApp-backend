import threading
import time
import Enums as enum
import client_socket_connection as client_socket_connection
import dhan_socket_connection as dhan_socket_connection
import json

class StatusChecker:
    def __init__(self,timeout,dhan,order_id,correlation_id,security_id,socket_id,socketIo):
        self.timeout = timeout
        self.last_response = None
        self.stop_event = threading.Event()
        self.dhan = dhan
        self.order_id = order_id
        self.correlation_id = correlation_id
        self.socket = socketIo
        self.security_id = security_id
        self.socket_id = socket_id

    def check_status(self):
        try:
            start_time = time.time()
            while not self.stop_event.is_set():
                response = self.dhan.get_order_by_id(order_id=self.order_id)
                status = response['data']['orderStatus']
                #if status != enum.Order_status.TRADED.name:
                if status == enum.Order_status.TRANSIT.name:
                    current_response = status  #Assuming the response is JSON
                    if self.last_response is not None and current_response == self.last_response:
                        if time.time() - start_time >= self.timeout:
                            self.cancel_request()
                            self.stop_event.set()
                            break
                    else:
                        self.last_response = current_response
                        start_time = time.time()
                else:
                    #dhan_socket_connection.subScribeSymbols(feed=self.dhanFeed, security_id=self.security_id)
                    #client_socket_connection.periodic_message(dhan_socket_connection.symbol_sub['security_id'])
                    print(response)
                    json_data = json.dumps(response)
                    self.socket.emit("order_status",json_data)
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
        

