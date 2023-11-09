import socket
import threading
import os

SERVER = None
IP_ADDRESS = '127.0.0.1'
PORT = 6000

CLIENTS = {}

def accept_connections():
    global CLIENTS
    global SERVER

    while True:
        player_socket, addr = SERVER.accept()
        player_name = player_socket.recv(1024).decode().strip()
        print(player_name)
        
        if len(CLIENTS.keys()) == 0:
            CLIENTS[player_name] = {'player_type': 'player1'}
        else:
            CLIENTS[player_name] = {'player_type': 'player2'}

        CLIENTS[player_name]["player_socket"] = player_socket
        CLIENTS[player_name]["address"] = addr
        CLIENTS[player_name]["player_name"] = player_name
        CLIENTS[player_name]["turn"] = False

        print(f"Connection established with {player_name} : {addr}")
        
        # Notify all clients about the new connection
        broadcast_message(f"{player_name} joined the chat!")

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(player_name, player_socket)).start()

def broadcast_message(message):
    global CLIENTS
    for client_name, client_info in CLIENTS.items():
        try:
            client_socket = client_info["player_socket"]
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting message to {client_name}: {e}")

def handle_client(player_name, player_socket):
    global CLIENTS
    while True:
        try:
            message = player_socket.recv(1024).decode('utf-8')
            if not message:
                break
            if "Download File:" in message:
                # Notify other clients about the file being sent
                broadcast_message(f"{player_name} sent a file: {message.split(':')[1]}")
            else:
                broadcast_message(f"{player_name}: {message}")
        except Exception as e:
            print(f"Error handling client {player_name}: {e}")
            break

    # If a client disconnects, remove them from the clients dictionary
    del CLIENTS[player_name]
    player_socket.close()
    broadcast_message(f"{player_name} left the chat.")

def setup():
    global SERVER
    global PORT
    global IP_ADDRESS

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS, PORT))
    SERVER.listen(10)

    print("\t\t\t\tSERVER IS WAITING FOR INCOMMING CONNECTIONS...\n")
    accept_connections()

setup()
