#programa basado en: https://youtu.be/NoxIdVvf4es

import bluetooth
import RPi.GPIO as GPIO #Libreria para el manejo de pines
GPIO.setmode(GPIO.BOARD)

host = "E4:5F:01:8B:EF:84"
port = 1

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server.bind((host, port))
server.listen(1)
cliente, direccion = server.accept()

while True:
    datos_preferencias = cliente.recv(1024)
    print(datos_preferencias)

    if datos_preferencias == 'Z':
        GPIO.cleanup()
        server.close()
        cliente.close()
        break