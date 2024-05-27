import threading
import socket
import asyncio
import websockets

clients = set()

async def register(websocket):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def handler(websocket, path):
    await register(websocket)

async def start_server():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # run forever

def send_message_to_clients(message):
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(broadcast_message(message), loop)

async def broadcast_message(message):
    if clients:
        await asyncio.gather(*(client.send(message) for client in clients))

async def periodic_message():
    while True:
        send_message_to_clients("Message from server")
        await asyncio.sleep(1)  # Sleep for 1 second

async def periodic_pong():
    while True:
        send_message_to_clients("pong")
        await asyncio.sleep(3)  # Send pong message every 3 seconds

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket server started at ws://localhost:8765")

    # Start the periodic message task
    asyncio.create_task(periodic_message())
    asyncio.create_task(periodic_pong())

    await server.wait_closed()



def run_server():
    def run_from_thread():
        asyncio.run(main())

    thread = threading.Thread(target=run_from_thread)
    thread.start()





 #normal Socket for Mobile clients    

def start_mobile_server(host='127.0.0.1', port=65432): 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
                if data.decode().strip() == 'ping':
                    conn.sendall(b'pong')
                else:
                    conn.sendall(b'Invalid message')



def run_start_server():
    def run_from_thread():
        result  = start_server()

    thread = threading.Thread(target=run_from_thread)
    thread.start()
       


# Create a TCP socket
def create_socket():
    my_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_address = ("localhost", 3131)
    my_socket.bind(host_address)

    my_socket.listen()
    # Wait for a connection and accept it
    connection, client_address = my_socket.accept()
    print("Connection received from:", client_address)
    return connection,my_socket

def message_loop(connection):
    # Receive and process messages from the client
    while True:
        data = connection.recv(1024)  # Receive data in chunks
       # if not data:
        #    break
        print("Received:", data.decode())  # Decode the received bytes
        response = str({"msg":"start_msg"})
        encoded_response = response.encode()
        connection.send(encoded_response)

def runSocketThread(connection):    
    def run_from_thread():
        message_loop(connection)

    thread = threading.Thread(target=run_from_thread)
    thread.start()
       
    

def send_message(connection,message : str):
    encoded_msg = message.encode()
    connection.send(encoded_msg)

def close_socket(socket,connection):
    connection.close()
    socket.close()
   



