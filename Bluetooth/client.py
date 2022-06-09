from bluetooth import *

server_addr = "xx:xx:xx:xx:xx:xx"
port = 1030
sock = BluetoothSocket(RFCOMM)
sock.connect((server_addr, port))

while True:
    response = sock.recv(1024)
    if len(response) == 0:
        break

print("received [%s]" % response)