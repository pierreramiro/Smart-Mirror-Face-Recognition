import socket
host = '10.100.108.56'
port = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)
print(f"Server's ip: {host}\n Server's port: {port}")
print(f"Waiting for incoming connections...")
client, addr = sock.accept()
print(f"{addr} connected")