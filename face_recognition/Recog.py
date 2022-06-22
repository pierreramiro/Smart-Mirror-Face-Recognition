import sys
from tkinter import Button

from click import echo
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Librería para el control del Raspberry
import RPi.GPIO as gpio
gpio.setwarnings(False)

import time

#Liberia para

class Window(QWidget):
    def __init__(self):
        super().__init__()
        #Configuramos los pines de la raspberry
        self.setupRaspberry()
        self.setWindowTitle("Face Recog.")
        #Resize window
        self.resize(400, 600)
        #Creamos variables
        self.maxDistance= 150#maxima distancia en cm
        self.maxTimeEcho= self.maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO
        # Create a QVBoxLayout instance
        layout = QVBoxLayout()
        #Creamos el boton
        self.push_button_start=QPushButton("Start")
        self.push_button_start.height=100
        self.push_button_start.width=100
        # Add widgets to the layout
        layout.addWidget(self.push_button_start)
        # Set the layout on the application's window
        self.setLayout(layout)
        #Conectamos los eventos con funciones
        self.push_button_start.pressed.connect(self.buttonPressed)
        #Timer para escuchar al SENSOR ULTRASONIDO
        self.timer_HCSR = QTimer()
        self.timer_HCSR.timeout.connect(self.sondeaSensor)
        self.timer_HCSR.start(100)#chequeamos la distancia cada 100ms

    def buttonPressed(self):
        print("Presionaste")
    def sondeaSensor(self):
        #medimos la distancia del sensor ultrasonido
        #tiempo de muestreo
        gpio.output(self.TRIGpin,gpio.HIGH)
        t1=time.time()
        #esperamos a cumplir los 10usec
        while time.time()<t1+0.000015:
            pass
        gpio.output(self.TRIGpin,gpio.LOW)
        #Esperamos el echo en HIGH
        while not(gpio.input(self.ECHOpin)):
            pass
        t1=time.time()
        #Esperamos el echo en flanco de bajada
        while gpio.input(self.ECHOpin):
            pass
        runnningTime=(time.time()-t1)*1000000
        if runnningTime<self.maxTimeEcho: 
            #Tenemos una persona en frente!

            #Procedemos a realizar el face recognition
            1
            


    def setupRaspberry(self):
        gpio.setmode(gpio.BCM)
        ######## CONTROL SENSOR #######
        self.ECHOpin=12
        self.TRIGpin=16
        #Configuramos como entrada
        gpio.setup(self.ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
        #Configuramos como salida
        gpio.setup(self.TRIGpin,gpio.OUT)
        gpio.output(self.TRIGpin,gpio.LOW)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_()) 