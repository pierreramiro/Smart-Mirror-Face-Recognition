import socket

host = "10.100.108.56" #IP of PUCP. Should be check with ´$ ip a´ 
port = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host,port))
print("You are connected!")