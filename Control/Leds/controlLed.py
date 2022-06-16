#Importamos libreras
import RPi.GPIO as gpio
import time

LREDpin=18
LGREENpin=23
LBLUEpin=24
#Configuramos la convecion de pines
gpio.setmode(gpio.BCM)
#Configuramos como salidas  
gpio.setup(LREDpin,gpio.OUT)
gpio.setup(LGREENpin,gpio.OUT)
gpio.setup(LBLUEpin,gpio.OUT)
#Configuramos todo en LOW
gpio.output(LREDpin,gpio.LOW)
gpio.output(LGREENpin,gpio.LOW)
gpio.output(LBLUEpin,gpio.LOW)

rojo=[gpio.HIGH,gpio.LOW,gpio.LOW]
verde=[gpio.LOW,gpio.HIGH,gpio.LOW]
azul=[gpio.LOW,gpio.LOW,gpio.HIGH]
amarillo=[gpio.HIGH,gpio.HIGH,gpio.LOW]
cian=[gpio.LOW,gpio.HIGH,gpio.HIGH]
rosado=[gpio.HIGH,gpio.LOW,gpio.HIGH]
blanco=[gpio.HIGH,gpio.HIGH,gpio.HIGH]
colores=["rojo","verde","azul","amarillo","cian","rosado","blanco"]
coloresGPIO=[rojo,verde,azul,amarillo,cian,rosado,blanco]
while True:
    #main
    color="blanco"
    #ponemos color
    idColor=colores.index(color)
    gpio.output(LREDpin,coloresGPIO[idColor][0])
    gpio.output(LGREENpin,coloresGPIO[idColor][1])
    gpio.output(LBLUEpin,coloresGPIO[idColor][2])
