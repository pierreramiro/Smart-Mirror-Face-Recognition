#programa basado en: https://youtu.be/UXzC5jAOmMA

import RPi.GPIO as GPIO #Libreria para el manejo de pines
import time

#Configuracion de pines
GPIO.setmode(GPIO.BCM)

Trigger = 16 #Numero de pin de Raspberry que va conectado al Trigger del sensor
Echo = 12 #Numero de pin de Raspberry que va conectado al Echo del sensor

GPIO.setup(Trigger, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)
detectado=0

detectado=0
while True:
    #tiempo de muestreo
    GPIO.output(Trigger,False)
    time.sleep(0.1)

    #onda se envia por un instante y luego se deja de enviar
    GPIO.output(Trigger,True)
    time.sleep(0.00001)
    GPIO.output(Trigger,False)
    inicio=time.time()

    #para definir el instante en el que se envio y que se recibe
    while GPIO.input(Echo)==0:
    #   inicio=time.time()
        pass#print("")

    while GPIO.input(Echo) == 1:
        final = time.time()

    #calculos para la distancia
    tiempo_transcurrido=final-inicio #tiempo total entre el envio de la onda hasta su recepcion

    distancia=tiempo_transcurrido*34000 #para hallar la distancia total recorrida por la onda
    distancia=distancia/2 #se divide entre 2 pues la distancia del obstaculo es la mitad de la recorrida

    time.sleep(1)
    print(distancia)
    # if distancia<20: #Numero que define la distancia a la que debe estar el usuario
    #     detectado=1
    #     break


