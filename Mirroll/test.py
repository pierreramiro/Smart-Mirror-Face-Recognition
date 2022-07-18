#!/usr/bin/env python3
import sys
from MainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
import time
import csv
#Librería para el control del Raspberry
import serial #uart

#Libreria para face recognition
import cv2
from face_recognition import face_encodings as FR_face_encodings
from face_recognition import face_locations as FR_face_locations
from face_recognition import compare_faces as FR_compare_faces
import pickle
from imutils.video import VideoStream
from imutils import resize as imResize
#Variable globales para la temperatura
import requests
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
CITY = "Lima"
API_KEY = "29244f2262bb6898c19715b2ae7ca9dc"
# upadting the URL
URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY

#Variables globales
noColor=[False,False,False]# noColor=[gpio.LOW,gpio.LOW,gpio.LOW]
rojo=[False,True,False]# rojo=[gpio.LOW,gpio.HIGH,gpio.LOW]
verde=[True,False,False]# verde=[gpio.HIGH,gpio.LOW,gpio.LOW]
azul=[False,False,True]# azul=[gpio.LOW,gpio.LOW,gpio.HIGH]
amarillo=[True,True,False]# amarillo=[gpio.HIGH,gpio.HIGH,gpio.LOW]
cian=[True,False,True]# cian=[gpio.HIGH,gpio.LOW,gpio.HIGH]
rosado=[False,True,True]# rosado=[gpio.LOW,gpio.HIGH,gpio.HIGH]
blanco=[True,True,True]# blanco=[gpio.HIGH,gpio.HIGH,gpio.HIGH]
colores=["noColor","rojo","verde","azul","amarillo","cian","rosado","blanco"]
coloresGPIO=[noColor,rojo,verde,azul,amarillo,cian,rosado,blanco]
#Face Recog resources
imagenesFaceRecognition = ['RostroIzq','RostroIzqMID','RostroFrente','RostroDerMID','RostroDer','RostroArriba']
imagenesProcessing=["Procesando1.png","Procesando2.png","Procesando3.png","Procesando4.png","Procesando5.png","Procesando6.png"]
#foldar names dataset
usersFolder=["user0","user1","user2","user3","user4","user5","user6","user7","user8","user9"]
#variables globales
STEPTIME=125000/2#en nanosec #Se tiene una velocidad de 2cm/seg
pulsesPerRev=1600 #con 3.5A
distPerRev=0.515 #en cm
PULSES_PER_DIST=pulsesPerRev/distPerRev
#Tamaño de la ventana
WIDTH_SCREEN=1920
HEIGHT_SCREEN=1080
#max altura
MAXIMA_ALTURA_ESPEJO=20
MINIMA_ALTURA_ESPEJO=0
#Variable para el repo
PATH_REPO='/home/mirroll/Documents/Github/Smart-Mirror-Face-Recognition'
#PATH_REPO='/home/pierreramiro/Documents/Github/Smart-Mirror-Face-Recognition'
# PATH_REPO='/home/catolica/Documents/Github/Smart-Mirror-Face-Recognition'


dato=1

class sleepModeDialog(QtWidgets.QDialog):
    def __init__(self,parent=None,val=0):
        super(sleepModeDialog,self).__init__(parent)

        self.setCursor(QtCore.Qt.BlankCursor)
        self.val=val
        #nombre a la ventana
        self.setWindowTitle("Sleep!")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        #Establecemos el tamaño de la pantalla
        self.setGeometry(0,0, WIDTH_SCREEN, HEIGHT_SCREEN)
        #Creo un layout
        self.layout = QtWidgets.QVBoxLayout()
        # loading image
        image = QImage('resources/Bt.png')
        image=image.scaled(int(WIDTH_SCREEN/1.5), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)
        # Configuramos el layout
        self.setLayout(self.layout)
        self.timer=QTimer()
        self.timer.timeout.connect(self.initClass)
        self.timer.start(1000)
        self.parent().newVal=11

    def initClass(self):
        self.timer.stop()
        for i in range(2):
            time.sleep(1)
            #print("Tiempo transcurrido:",i)
        time.sleep(1)
        #print("Cerramos el sleep")
        self.close()
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

class warningBox (QtWidgets.QDialog):
    def __init__(self,parent=None,val=0):
        super(warningBox,self).__init__(parent)

        self.setCursor(QtCore.Qt.BlankCursor)
        self.val=val
        #nombre a la ventana
        self.setWindowTitle("HELLO!")
        #Creo un layout
        self.layout = QtWidgets.QVBoxLayout()
        # loading image
        image = QImage('resources/facePostions.jpeg')
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(self.imageLabel)
        # Configuramos el layout
        self.setLayout(self.layout)
        self.timer=QTimer()
        self.timer.timeout.connect(self.CloseWarning)
        self.timer.start(1000)

    def CloseWarning(self):
        #print("Valor despues de crear la notificacion: ",self.val)
        #self.parent().imprime()
        self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

class Gui(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        #Creamos nuestra GUI
        #self.setCursor(QtCore.Qt.BlankCursor)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        self.dato=dato
        self.button = QtWidgets.QPushButton("Press me for a dialog!",self.ui.frame_2)
        self.button.setGeometry(QtCore.QRect(WIDTH_SCREEN-500, HEIGHT_SCREEN-500, 200, 200))
        self.button.clicked.connect(self.button_clicked)
        self.startVal=True
        self.time1=QTimer()
        self.time1.timeout.connect(self.initMirroll)
        self.time1.start(10)

    def initMirroll(self):
        self.time1.stop()
        dlg = sleepModeDialog(self)
        dlg.show()
        from git import Repo
        repo = Repo(PATH_REPO)
        origin = repo.remote(name='origin')
        origin.pull()
        

    def button_clicked(self, s):
        #print("click", s)
        #print("Valor antes de cerrar la notificacion: ",self.newVal)
        f=open("archivoDePrueba.txt","w")
        dlg = warningBox(self,val=5)
        dlg.show()
        f.close()
        """actualizamos git"""
        from git import Repo
        repo = Repo(PATH_REPO)
        #añadimos todos los archivos modificados
        repo.git.add('--all')
        #Añadimos comentario
        t=repo.head.commit.tree
        if len(list(repo.git.diff(t)))>0:
            repo.git.commit('-m', 'boton pressed')
            origin = repo.remote(name='origin')
            origin.push()

stylesheet="""
    QMainWindow{
        background:black
    }
"""

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(stylesheet)
window = Gui()
window.show()
sys.exit(app.exec())


