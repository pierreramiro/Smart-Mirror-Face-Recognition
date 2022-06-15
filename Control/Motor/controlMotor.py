
#Importamos libreras
import RPi.GPIO as gpio
import time

#Configuramos la convecion de pines
gpio.setmode(gpio.BCM)
######## CONTROL MOTOR #######
ENApin=17
DIRpin=27
PULpin=22
LSUPpin=5
LSDOWNpin=6
#Configuramos como salidas
gpio.setup(ENApin,gpio.OUT)
gpio.setup(DIRpin,gpio.OUT)
gpio.setup(PULpin,gpio.OUT)
#Configuramos todo en LOW
gpio.output(ENApin,gpio.HIGH)
gpio.output(DIRpin,gpio.LOW)
gpio.output(PULpin,gpio.LOW)






def BajarEspejo(altura=-1,STEPTIME=125/2*1000): #STEPTIME debe estar en nanosecs
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.HIGH)
    if altura==-1:
        #Bajamos el espejo hasta sentir el limit switch
        while gpio.input(LSDOWNpin)!=0:
            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<STEPTIME:
                pass

            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<STEPTIME:
                pass
    else:
        #Bajamos una cierta altura
        """Es similar al anterior, solo que en vez de un while para checar el limit, se le añade la distanciaa estimada por calculo del factor de pulsos/m"""
    #Deshabilitamos el driver del motor
    gpio.output(ENApin,gpio.HIGH)


def SubirEspejo(altura=-1,STEPTIME=125/2*1000): #STEPTIME debe estar en nanosecs
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.HIGH)
    if altura==-1:
        #Bajamos el espejo hasta sentir el limit switch
        while gpio.input(LSDOWNpin)!=0:
            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<STEPTIME:
                pass

            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<STEPTIME:
                pass
    else:
        #Bajamos una cierta altura
        """Es similar al anterior, solo que en vez de un while para checar el limit, se le añade la distanciaa estimada por calculo del factor de pulsos/m"""
    #Deshabilitamos el driver del motor
    gpio.output(ENApin,gpio.HIGH)


#Bajamos el espejo hasta sentir el limit switch
while True:
    BajarEspejo()
