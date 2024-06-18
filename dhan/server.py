from websocket_server import WebsocketServer
import json

# Called for every client connecting (after handshake)
def new_client(client, server:WebsocketServer):
	print("New client connected and was given id %d" % client['id'])
	server.send_message_to_all("Hey all, a new client has joined us")
	server.send_message(client,json.dumps({'type' : 'IDAM' , 'data' : {'socket_client_id': client['id']}}))


# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
	if len(message) > 200:
		message = message[:200]+'..'
	print("Client(%d) said: %s" % (client['id'], message))

def send_message(message,client_id):
	client = active_server.client_dict[client_id]
	active_server.send_message(client,message)
	

def init_and_run_server():
	PORT=8765
	global active_server
	active_server = WebsocketServer(port = PORT)
	active_server.set_fn_new_client(new_client)
	active_server.set_fn_client_left(client_left)
	active_server.set_fn_message_received(message_received)
	active_server.run_forever()


# for testing purpose only 
def init_and_run():
	PORT=8765
	global active_server
	active_server = WebsocketServer(port = PORT)
	active_server.set_fn_new_client(new_client)
	active_server.set_fn_client_left(client_left)
	active_server.set_fn_message_received(message_received)
	active_server.run_forever()

if(__name__ == '__main__'):
    init_and_run()
