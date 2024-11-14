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
            print(f"Requesting File {file_name}, From {target_client}")
            client_socket.send(f"REQUEST_FILE {target_client} {file_name}".encode())
        
        elif command.upper() == "EXIT":
            client_socket.send("DISCONNECT".encode())
            break
        elif command.lower().startswith("me"):
                print(client_socket.getsockname())

def receive_responses():
    while True:
        try:
            response = client_socket.recv(1024).decode()
            print(response)
            # Conditional Block for the requested file
            if response.startswith("FILE_REQUEST"):
                print(response, response.split())
                _, file_name,requestor_addr = response.split(maxsplit=2)
                requestor_addr = ast.literal_eval((requestor_addr))

                print(f"Received a file request for {file_name} from {requestor_addr}")
                file_path = os.path.join("../data/", file_name)
                if os.path.exists(file_path):
                    client_socket.sendall(f"SENDING_FILE {file_name} {requestor_addr}".encode())
                    chunk_length = 0
                    with open(f"../data/{file_name}", "rb") as file:
                        chunk = file.read(1024)
                        print("Sending the data of file of type: ", type(chunk))
                        while chunk:
                            chunk_length = chunk_length + len(chunk)
                            if not chunk:
                                print("Sender recived EOF")
                                break
                            client_socket.sendall(chunk)
                            chunk = file.read(1024)

                    client_socket.sendall(b"F-201")
                    print("Sent chunk of total lenght of: ", chunk_length)
                else:
                    client_socket.sendall("File not found.".encode())
            
            # Conditional Block for Reciving the incoming
            elif response.startswith("SENDING_FILE"):
                _, file_name = response.split()
                print(f"Receiving file '{file_name}'...")                
                # Create or open the file to write the incoming data
                recv_chunk_length = 0
                with open(f"../data/received_{file_name}", "wb") as file:
                    try:
                        while True:
                                data = client_socket.recv(1024)
                                recv_chunk_length = recv_chunk_length + len(data)
                                print("Reciving data of file of type: ", type(data))
                                if data == b"F-201":  # End of file transmission
                                    print(f"*********File '{file_name}' received successfully.***********")
                                    break
                                file.write(data)
                                print("Requestor recived chunk size of: ",recv_chunk_length)
                    except Exception as e:
                        print(f"Error while trying to write: {e}")
                        break
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