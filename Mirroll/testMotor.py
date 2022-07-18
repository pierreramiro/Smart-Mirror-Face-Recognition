
#Importamos libreras
import RPi.GPIO as gpio
import time

STEPTIME=125000/2 #en nanosegundos
#STEPTIME=15000 #en nanosegundos
pulsesPerRev=1600 #3.5A
distPerRev=0.515 #En cm
PULSES_PER_DIST=pulsesPerRev/distPerRev
VELOCIDAD_SUBIDA= 0.1#en cm/seg
#STEPTIME=1000000/(PULSES_PER_DIST*VELOCIDAD_SUBIDA)
MAXIMA_ALTURA_ESPEJO=20
MINIMA_ALTURA_ESPEJO=0

def Subir10Rev():
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.HIGH)
    for i in range(10*pulsesPerRev):    
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

def Bajar10Rev():
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.LOW)
    for i in range(10*pulsesPerRev):  
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


def BajarEspejo(distancia=-1): 
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.LOW)
    #Primero iniciamos con un step time para una velocidad a la mitad de la de bajada
    initSteptime=STEPTIME*2 #En este caso será de de 1cm/seg la velocidad de subida
    #Luego de cierto tiempo aumentamos la velocidad a 2cm/seg
    timeSlowStep=2#en segundos
    initPulsesInSlow=(timeSlowStep*1000000000)/(initSteptime*2)#Para el caso de 1seg tenemos un total de 4000 pulsos
    tempSteptime=initSteptime
    adderStepTime=(STEPTIME-initSteptime)/initPulsesInSlow
    if distancia==-1:
        #Bajamos el espejo hasta sentir el limit switch
        while gpio.input(LSDOWNpin)==0:
            if tempSteptime<=STEPTIME:
                tempSteptime=STEPTIME
            else:
                tempSteptime+=adderStepTime
            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass

            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
        actualAltura=MINIMA_ALTURA_ESPEJO
    else:
        #Bajamos una cierta altura o hasta sentir el Limit switch
        for i in range(int(distancia*PULSES_PER_DIST)):
            if tempSteptime<=STEPTIME:
                tempSteptime=STEPTIME
            else:
                tempSteptime+=adderStepTime
            
            #Verificamos limit SW
            if gpio.input(LSDOWNpin)!=0:
                actualAltura=MINIMA_ALTURA_ESPEJO
                break

            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
            
            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
            #Verificamos limit SW
            if gpio.input(LSDOWNpin)!=0:
                actualAltura=MINIMA_ALTURA_ESPEJO
                break
    gpio.output(ENApin,gpio.HIGH)

def SubirEspejo(distancia=-1): 
    #Habilitamos el driver del motor
    gpio.output(ENApin,gpio.LOW)
    #Definimos la dirección
    gpio.output(DIRpin,gpio.HIGH)
    #Primero iniciamos con un step time para una velocidad a la mitad de la de bajada
    initSteptime=STEPTIME*2 #En este caso será de de 1cm/seg la velocidad de subida
    #Luego de cierto tiempo aumentamos la velocidad a 2cm/seg
    timeSlowStep=2#en segundos
    initPulsesInSlow=(timeSlowStep*1000000000)/(initSteptime*2)#Para el caso de 1seg tenemos un total de 4000 pulsos
    tempSteptime=initSteptime
    adderStepTime=(STEPTIME-initSteptime)/initPulsesInSlow
    if distancia==-1:
        #Subimos el espejo hasta sentir el limit switch
        while gpio.input(LSUPpin)==0:#notar que se detiene en flanco de subida!
            if tempSteptime<=STEPTIME:
                tempSteptime=STEPTIME
            else:
                tempSteptime+=adderStepTime
            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
        actualAltura=MAXIMA_ALTURA_ESPEJO
    else:
        #Subimos el espejo una cierta altura o hasta sentir el limit switch
        for i in range(int(distancia*PULSES_PER_DIST)):
            if tempSteptime<=STEPTIME:
                tempSteptime=STEPTIME
            else:
                tempSteptime+=adderStepTime
            #Verificamos limit SW
            if gpio.input(LSUPpin)!=0:
                actualAltura=MAXIMA_ALTURA_ESPEJO
                break
            #Ponemos en HIGH
            gpio.output(PULpin,gpio.HIGH)        
            #Esperamos en HIGH
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
            
            #Ponemos en LOW
            gpio.output(PULpin,gpio.LOW)        
            #Esperamos en LOW
            initTime=time.time_ns()
            while time.time_ns()-initTime<tempSteptime:
                pass
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

    #Subir10Rev()
    while True:
        print(gpio.input(LSUPpin))
        #gpio.output(ENApin,gpio.HIGH)
        #gpio.output(DIRpin,gpio.LOW)
        #gpio.output(PULpin,gpio.HIGH)
        BajarEspejo(1)    
        #SubirEspejo(1)
