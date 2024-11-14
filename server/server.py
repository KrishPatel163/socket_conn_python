import socket
import threading
import ast

server_host = "localhost"
server_port = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_host, server_port))
server_socket.listen(5)

print("Server is listening...")

server_running = True
connected_clients = []
available_sockets = []
client_ids = {}

def handle_client(client_socket, client_addr):
    print(f"New client joined: {client_addr}")
    connected_clients.append(client_addr)
    available_sockets.append(client_socket)
    client_ids[client_addr] = client_socket
    
    client_socket.send("Welcome to the server!".encode())
    
    try:
        while True:
            data = client_socket.recv(1024).decode()
            print(data)
            if not data:
                break
            if data.startswith("REQUEST_FILE"):
                _, target_client, file_name = data.split()
                print(target_client)
                if target_client.startswith("(") and target_client.endswith(")"):
                    target_client = f"('{target_client[1:].split(',')[0]}',{target_client.split(',')[1]}"
                
                target_client = ast.literal_eval(target_client)
                
                if target_client in client_ids:
                    target_client_socket = client_ids[target_client]
                    target_client_socket.send(f"FILE_REQUEST {file_name} {client_addr}".encode())
                else:
                    client_socket.send("Target client not found.".encode())
                    
            elif data.startswith("SENDING_FILE"):
                _, file_name, requestor_addr = data.split(maxsplit=2)
                requestor_addr = ast.literal_eval(requestor_addr)

                if requestor_addr in client_ids:
                    requestor_socket = client_ids[requestor_addr]
                    # Notify the requester that file transfer is starting
                    requestor_socket.send(f"SENDING_FILE {file_name}".encode())
                    
                    # Relay file data from sender to requester
                    chunk_size = 0
                    while True:
                        chunk = client_socket.recv(1024)
                        print(chunk)
                        chunk_size = chunk_size + len(chunk)
                        if not chunk:  # End of file transmission
                            print("Server sensed end of file.")
                            requestor_socket.send(b"F-201")
                            break
                        requestor_socket.send(chunk)
                        print("Server Recived the chunk size of: ",chunk_size)
                else:
                    client_socket.send("Requesting client not connected.".encode())

            
    except ConnectionResetError:
        print(f"{client_addr} disconnected abruptly.")
    finally:
        print(f"Client {client_addr} left the session. ")
        connected_clients.remove(client_addr)
        available_sockets.remove(client_socket)
        del client_ids[client_addr]
        print(f"Remaining clients are: {connected_clients}")
        client_socket.close()

def listen_for_shutdown():
    global server_running
    while server_running:
        command = input("Enter 'shutdown' to stop the server: ")
        if command.lower() == 'shutdown':
            print("Shutting down the server...")
            server_running = False

            # Close all active client connections
            for client in available_sockets:
                client.close()
            server_socket.close()
            break

shutdown_thread = threading.Thread(target=listen_for_shutdown)
shutdown_thread.start()

while server_running:
    try:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    except OSError:
        break
    
shutdown_thread.join()
print("Server has been shut down.")