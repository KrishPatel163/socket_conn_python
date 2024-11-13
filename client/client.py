import socket as sc
import threading
import os
import ast
from datetime import datetime

client_host = "127.0.0.1"
client_port = 9999

client_socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
client_socket.connect((client_host, client_port))

def send_requests():
    while True:
        command = input("Enter command (REQUEST_FILE or EXIT): ")
        
        if command.startswith("REQUEST_FILE"):
            target_client = input("Enter target client address in format (host, port): ")
            file_name = input("Enter filename to request: ")
            client_socket.send(f"REQUEST_FILE {target_client} {file_name}".encode())
        
        elif command.upper() == "EXIT":
            client_socket.send("DISCONNECT".encode())
            break

def receive_responses():
    while True:
        try:
            response = client_socket.recv(1024).decode()
            
            # Conditional Block for the requested file
            if response.startswith("FILE_REQUEST"):
                _, file_name, requestor_addr = response.split()
                requestor_addr = ast.literal_eval(requestor_addr)

                print(f"Received a file request for {file_name} from {requestor_addr}")
                if os.path.exists(file_name):
                    client_socket.sendall(f"SENDING_FILE {file_name} {requestor_addr}".encode())
                    with open(f"../data/{file_name}", "rb") as file:
                        chunk = file.read(1024)
                        while chunk:
                            client_socket.sendall(chunk)
                            chunk = file.read(1024)
                    client_socket.sendall(b"DONE")
                else:
                    client_socket.sendall("File not found.".encode())
            
            # Conditional Block for Reciving the incoming
            elif response.startswith("SENDING_FILE"):
                _, file_name = response.split()
                print(f"Receiving file '{file_name}'...")
                
                # Create or open the file to write the incoming data
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                new_file_name = f"{file_name}-{timestamp}"
                with open(f"../data/received_{new_file_name}", "wb") as file:
                    while True:
                        data = client_socket.recv(1024)
                        if data == b"DONE":  # End of file transmission
                            print(f"File '{file_name}' received successfully.")
                            break
                        file.write(data)
            else:
                print("Server:", response)

        except ConnectionResetError:
            break
        
send_thread = threading.Thread(target=send_requests)
receive_thread = threading.Thread(target=receive_responses)
send_thread.start()
receive_thread.start()

send_thread.join()
client_socket.close()