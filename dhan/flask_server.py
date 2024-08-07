from flask import Flask,request
import super_app as my_app
from flask_cors import CORS
from flask import make_response, render_template
from flask_socketio import SocketIO, send 
import multiprocessing
import threading
from status_checker import StatusChecker
import json
from logger import logger

api = "127.0.0.1:8000"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, message_queue='amqp://guest:guest@localhost:5672/',cors_allowed_origins = "*")
cors = CORS(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')#Content-Type,Authorization
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  response.headers.add('Access-Control-Expose-Headers' , 'x-request-type') # * to expose all headers to client
  return response

@app.route('/orders', methods=["GET"])
def getAllOrders():
    return my_app.getOrders()

@app.route('/openOrders', methods=["GET"])
def getAllOpenOrders():
    result = my_app.get_open_orders()
    response = {}
    response["data"] = result
    data =  make_response(json.dumps(response));
    return data

@app.route('/orderstatus', methods=["GET"])
def get_order_status():
    order_id = request.args.get('order_id')
    data = my_app.get_order_status(order_id)
    response = make_response(data)
    #response.headers['x-request-type'] = 'orderstatus'
    return response

@app.route('/openPosition', methods=["GET"])
def getOpenPosition():
    return my_app.get_open_positions()

@app.route('/closePosition', methods=["GET"])
def closePosition():
    security_id = request.args.get('security_id')
    exchange_segment = request.args.get('exchange_segment')
    transaction_type = request.args.get('transaction_type')
    quantity = request.args.get('quantity')
    product_type = request.args.get('product_type')

    data = my_app.closeAllPositions(security_id=security_id,exchange_segment=exchange_segment,transaction_type=transaction_type,quantity=quantity,product_type=product_type)
    response = make_response(data)
   
    #response.headers['x-request-type'] = 'closePosition'
    return response
 

@app.route('/placeOrder', methods=["GET"])
def placeOrder():
    
    index_name = request.args.get('index')
    option_type = request.args.get('option_type')
    transaction_type = request.args.get('transaction_type')
    client_order_id = request.args.get('client_order_id')
    socket_client_id = request.args.get('socket_client_id')
    dhan_client_id  = request.args.get('dhan_client_id')
    product_type = request.args.get('product_type')
    
    data = my_app.placeOrder(index_name=index_name,option_type=option_type,transaction_type=transaction_type,dhan_client_id=dhan_client_id,client_order_id=client_order_id,product_type=product_type)
   
    logger.info(data)
    # if not data and not data['data']['orderId']:

    #     order_id = data['data']['orderId'] 
    #     security_id =data['security_id']
    #     checker = StatusChecker(timeout= 5,dhan= my_app.dhan,correlation_id=client_order_id,order_id=order_id,security_id=security_id,socket_id=socket_client_id,socketIo=socketio)
    #     checker.start()
   # response.headers['x-request-type'] = 'placeOrder'
    data['client_order_id'] = client_order_id
    response = make_response(data)
    return response

@app.route('/addLevels', methods=["GET"])
def add_trade_level():
    index_name = request.args.get('index_name')
    option_type = request.args.get('option_type')
    price_level = request.args.get('price_level')
    dhan_client_id  = request.args.get('dhan_client_id')
    id = request.args.get('id');

    result = my_app.add_trade_level(id =id,index_name = index_name,option_type= option_type,price_level=price_level,dhan_client_id = dhan_client_id)
    response = {}
    response["data"] = result
    data =  make_response(json.dumps(response));
    
    return data


@app.route('/getLevels', methods=["GET"])
def get_trade_level():
    dhan_client_id  = request.args.get('dhan_client_id')
    data = my_app.get_trade_levels(dhan_client_id=dhan_client_id)
    response = {}
    response["data"] = data
    return make_response(json.dumps(response))

@app.route('/deleteLevels', methods=["GET"])
def delete_trade_level():
    index_name = request.args.get('index_name')
    price_level = request.args.get('price_level')
    dhan_client_id  = request.args.get('dhan_client_id')

    my_app.delete_trade_levels(dhan_client_id=dhan_client_id,index_name=index_name,level=price_level)
    response = {}
    response["data"] = {"result":"success"}
    return make_response(json.dumps(response))

@app.route('/fundLimits', methods=["GET"])
def fundLimit():
    return my_app.getFundLimit()

@app.route('/')
def flask_server():
    return 'hello_world'


def start_dhan_feed():
    global parent_conn
    global child_conn

    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(target=my_app.run_dhan_feed,args=(child_conn,))
    process.daemon = True  # Daemonize process to exit with the main program
    process.start()

    receiver_thread(parent_conn)
    
    #process.join()   # wait for process to complete and join main thread

def receiver_thread(conn):
    thread = threading.Thread(target=receiver, args=(conn,))
    thread.start()
    return thread

def receiver(conn):
   while True:
       msg = conn.recv()
       if msg == "STOP":
            break
       
       send_msg_via_socket_io(msg)
       process_feed(my_app.market_feed_callback,msg) # callback to super_app 

def process_feed(callback,msg):
    callback(msg)

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

def send_msg_via_socket_io(msg):
    socketio.emit('market_feed',msg)    

if __name__ == '__main__' :
    my_app.init()
    start_dhan_feed()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
   # app.run(debug=False)
   
def main():
    my_app.init()
    start_dhan_feed()