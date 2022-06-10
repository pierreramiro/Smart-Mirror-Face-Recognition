import bluetooth

#analizamos los dispositivos encontrados
nearby_devices = bluetooth.discover_devices()
#imprimimos los dispositivos encontrados
for bdaddr in nearby_devices:
  print(str(bluetooth.lookup_name( bdaddr))+" ["+str(bdaddr)+"]")
opt=input("cual es su dispositivo?")
#Establecemos un soccket para establecer la conexión
server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
#Establecemos un puerto
port = 1
#creamos el socket
server_sock.bind(("",port))
#escuchamos y buscamos la conexión
server_sock.listen(1)
#aceptamos al device
client_sock,address = server_sock.accept()
#imprimos con quien estamos conectados
print ("Accepted connection from " + str(address))
# #
# data = client_sock.recv(1024)
# print ("received [%s]" % data)
# client_sock.close()

# server_sock.close()