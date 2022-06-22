import sys
from tkinter import Button
from turtle import distance

from click import echo
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Librería para el control del Raspberry
import RPi.GPIO as gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
######## CONTROL SENSOR #######
ECHOpin=12
TRIGpin=16
#Configuramos como entrada
gpio.setup(ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
#Configuramos como salida
gpio.setup(TRIGpin,gpio.OUT)
gpio.output(TRIGpin,gpio.LOW)
maxDistance= 150#maxima distancia en cm
maxTimeEcho= maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO
        
import time

def sondeaSensor():
    #medimos la distancia del sensor ultrasonido
    #tiempo de muestreo
    gpio.output(TRIGpin,gpio.HIGH)
    t1=time.time()
    #esperamos a cumplir los 10usec
    while time.time()<t1+0.000015: #nosotros esperamos hasta 15us
        pass
    gpio.output(TRIGpin,gpio.LOW)
    #Esperamos el echo en HIGH
    while not(gpio.input(ECHOpin)):
        pass
    t1=time.time()
    #Esperamos el echo en flanco de bajada
    while gpio.input(ECHOpin):
        pass
    runnningTime=(time.time()-t1)*1000000
    if runnningTime<maxTimeEcho: 
        #Tenemos una persona en frente!
        print("distancia:",runnningTime*0.034/2)
        #Procedemos a realizar el face recognition
            

if __name__ == "__main__":
    while True:
        time.sleep(0.1)
        sondeaSensor()