from flask import Flask,request
from flask_cors import CORS
from flask import make_response 
import multiprocessing


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


@app.route('/')
def flask_server():
    return 'hello_world'

if __name__ == '__main__' :
    app.run(debug=False)