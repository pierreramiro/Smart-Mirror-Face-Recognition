
#Importamos libreras
import RPi.GPIO as gpio
import time

def SubirEspejo(altura=-1,STEPTIME=125/4*1000): #STEPTIME debe estar en nanosecs
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.HIGH)
    if altura==-1:
        #Bajamos el espejo hasta sentir el limit switch
        while gpio.input(LSUPpin)==0:
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


def BajarEspejo(altura=-1,STEPTIME=125/4*1000): #STEPTIME debe estar en nanosecs
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.LOW)
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

if __name__=="__main__":
    #Bajamos el espejo hasta sentir el limit switch
    #Configuramos la convecion de pines
    gpio.setmode(gpio.BCM)
    ######## CONTROL MOTOR #######
    ENApin=17
    DIRpin=27
    PULpin=22
    #Configuramos como salidas
    gpio.setup(ENApin,gpio.OUT)
    gpio.setup(DIRpin,gpio.OUT)
    gpio.setup(PULpin,gpio.OUT)
    #Configuramos todo en LOW
    gpio.output(ENApin,gpio.HIGH)
    gpio.output(DIRpin,gpio.LOW)
    gpio.output(PULpin,gpio.LOW)

    ####limits
    gpio.setup(3,gpio.OUT)
    gpio.output(3,gpio.HIGH)
    LSUPpin=5
    LSDOWNpin=6
    #Configuramos como entradas
    gpio.setup(LSUPpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
    gpio.setup(LSDOWNpin,gpio.IN,pull_up_down=gpio.PUD_UP)

    while True:
        print(gpio.input(LSUPpin))
        #gpio.output(ENApin,gpio.HIGH)
        #gpio.output(DIRpin,gpio.LOW)
        #gpio.output(PULpin,gpio.HIGH)
        BajarEspejo()
        #SubirEspejo()
