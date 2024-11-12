import socket as sc
import threading

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
            if response.startswith("FILE_REQUEST"):
                print("File request received. Sending file...")
                # Logic to send the file back goes here
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