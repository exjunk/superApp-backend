from flask import Flask,request
import superApp as myApp
from flask_cors import CORS
from flask import make_response

api = "127.0.0.1:8000"
app = Flask(__name__)
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
    return myApp.getOrders()

@app.route('/orderstatus', methods=["GET"])
def get_order_status():
    order_id = request.args.get('order_id')
    data = myApp.get_order_status(order_id)
    response = make_response(data)
    response.headers['x-request-type'] = 'orderstatus'
    return response

@app.route('/openPosition', methods=["GET"])
def getOpenPosition():
    return myApp.get_open_positions()

@app.route('/closePosition', methods=["GET"])
def closePosition():
    security_id = request.args.get('security_id')
    exchange_segment = request.args.get('exchange_segment')
    transaction_type = request.args.get('transaction_type')
    quantity = request.args.get('quantity')
    product_type = request.args.get('product_type')

    data = myApp.closeAllPositions(security_id=security_id,exchange_segment=exchange_segment,transaction_type=transaction_type,quantity=quantity,product_type=product_type)
    response = make_response(data)
    response.headers['x-request-type'] = 'closePosition'
    return response
 

@app.route('/placeOrder', methods=["GET"])
def placeOrder():
    index_name = request.args.get('index')
    option_type = request.args.get('option_type')
    transaction_type = request.args.get('transaction_type')

    data = myApp.placeOrder(index_name,option_type,transaction_type)
    response = make_response(data)
    response.headers['x-request-type'] = 'placeOrder'
    return response

@app.route('/fundLimits', methods=["GET"])
def fundLimit():
    return myApp.getFundLimit()

@app.route('/')
def hello():
    return 'hello_world'

if(__name__ == '__main__'):
    app.run()