import socket
host = '10.100.108.56'
port = int(input("pon port: "))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)
print(f"Server's ip: {host}\n Server's port: {port}")
print(f"Waiting for incoming connections...")
client, addr = sock.accept()
data = client.recv(1024)
data= data.decode()
data=data.split('\n')
data=data[0] #eliminamos la demas infroación
print(data)
#Obtenemos el indice del caracter '?' del inicio de nuestra trama
idInit=0
while (0):
    # hacemos la comapracion
    if (data[idInit]=='¿'):
        break
    #aumentamos el contador ID
    idInit+=1
idInit+=1
#Obtenemos el indice del caracter '¿' del fin de nuestra trama
idFin=-1
while (0):
    # hacemos la comapracion
    if (data[idFin]=='?'):
        break
    #disminuimos el contador del ID
    idFin-=1
print("Limpieza (result): ", data[idInit:idFin])
print(f"{addr} connected")
client.send('Hola KenBALL'.encode())
client.close()