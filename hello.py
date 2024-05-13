from flask import Flask,request
import superApp as myApp
from flask_cors import CORS

api = "127.0.0.1:8000"
app = Flask(__name__)
cors = CORS(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/orders', methods=["GET"])
def getAllOrders():
    return myApp.getOrders()

@app.route('/placeOrder', methods=["GET"])
def placeOrder():
    index_name = request.args.get('index')
    option_type = request.args.get('option_type')
    transaction_type = request.args.get('transaction_type')
 #   print(index_name)
  #  print(option_type)
    return myApp.placeOrder(index_name,option_type,transaction_type)

@app.route('/')
def hello():
    return 'hello_world'

if(__name__ == '__main__'):
    app.run()