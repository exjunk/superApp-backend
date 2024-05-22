import threading
import socket


# Create a TCP socket
def create_socket():
    my_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_address = ("localhost", 3131)
    my_socket.bind(host_address)

    my_socket.listen()
    # Wait for a connection and accept it
    connection, client_address = my_socket.accept()
    print("Connection received from:", client_address)
    return connection,client_address

def message_loop(connection):
    # Receive and process messages from the client
    while True:
        data = connection.recv(1024)  # Receive data in chunks
        if not data:
            break
        print("Received:", data.decode())  # Decode the received bytes
        response = {"msg":"start_msg"}
        encoded_response = response.encode()
        connection.send(encoded_response)

       
    

def send_message(connection,message : str):
    encoded_msg = message.encode()
    connection.send(encoded_msg)

def close_socket(socket,connection):
    socket.close()
    connection.close()



