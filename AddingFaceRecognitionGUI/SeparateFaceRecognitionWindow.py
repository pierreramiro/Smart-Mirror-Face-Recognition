from ctypes import alignment
from platform import java_ver
import sys
from tkinter import Button
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

class Window(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        #Ponemos un nombre a la ventana3
        self.setWindowTitle("Reconocimiento Facial")
        self.setWindowIcon(QIcon('Resources/RFLogo.png'))
        self.resize(600, 600)
        #creo el layout de nuestra ventana (vertical)
        self.layout=QtWidgets.QVBoxLayout()
        #Creo el texto a mostrar
        message = QtWidgets.QLabel("Acérquese a la cámara")
        message.setStyleSheet("font: 16pt \"Arial Rounded MT Bold\";")
        message.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(message)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)
        #seteando variables
        self.j=0
        self.i=-1
        self.imageLabel = QtWidgets.QLabel()
        self.newmessage = QtWidgets.QLabel("Coloque su rostro como muestra la imagen")   

        self.timer_Datos=QTimer()
        self.timer_Datos.timeout.connect(self.cambiaImagen)
        self.timer_Datos.start(200)
        
    def cambiaImagen(self):
        
        self.j=self.j+1
        if self.i<0 and (self.j%15==0):
            self.newmessage.setStyleSheet("font: 21pt \"Arial Rounded MT Bold\";")
            self.newmessage.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.newmessage)
            self.layout.addWidget(self.imageLabel)
            self.i=self.i+1

        if self.i<len(imagenesFaceRecognition) and self.i>=0 and (self.j%15==0):
            image=QImage('Resources/'+imagenesFaceRecognition[self.i]+'.png')
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.setLayout(self.layout)
            self.i=self.i+1

        if (self.j%15)==13 and self.j>=28:
            image=QImage('Resources/CamP.png')
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.setLayout(self.layout)

        
imagenesFaceRecognition = ['RostroIzq','RostroIzqMID','RostroFrente','RostroDerMID','RostroDer','RostroArriba']



if __name__ == "__main__":
        
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_()) 