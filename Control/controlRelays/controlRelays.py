#Importamos libreras
import RPi.GPIO as gpio
import time

gpio.setwarnings(False)
CH1pin=10
CH2pin=9     
CH3pin=11

#Configuramos la convecion de pines
gpio.setmode(gpio.BCM)
#Configuramos como salidas  
gpio.setup(CH1pin,gpio.OUT)
gpio.setup(CH2pin,gpio.OUT)
gpio.setup(CH3pin,gpio.OUT)
#Configuramos todo en LOW
gpio.output(CH1pin,gpio.LOW)
gpio.output(CH2pin,gpio.LOW)
gpio.output(CH3pin,gpio.LOW)

while True:
    gpio.output(CH1pin,gpio.HIGH)
    gpio.output(CH2pin,gpio.HIGH)
    gpio.output(CH3pin,gpio.HIGH)
