from bluetooth import *

server_sock = BluetoothSocket(RFCOMM)

port = 1030
server_sock.bind(("xx:xx:xx:xx:xx:xx",port))
server_sock.listen(1)

client_sock,address = server_sock.accept()
print("Accepted connection from ", address)

f = open("database.txt", "r")

listOfUsers = {}

for line in f:
    email, password, firstName, lastName = line.strip().split(",")
    listOfUsers[email] = (password, firstName, lastName)

f.close()

server_sock.send(listOfUsers)

client_sock.close()
server_sock.close()