import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, QTime, QDate
import time

class mirroll_GUI(QMainWindow):

    def __init__ (self):
        super().__init__()
        uic.loadUi("gui_app3.ui",self)
        self.estadoS1=estadoS1
        self.estadoS2=estadoS2
        self.estadoS3=estadoS3
        #self.botonS1.setEnabled(estadoS1)
        #self.fecha.setText(fecha_actual)
        #self.hora.setText(hora_actual)
        self.temperatura.setText(temperatura_actual)        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.displayFecha)
        self.timer.timeout.connect(self.displayHora)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(1000)

    def displayHora(self):
        currentHora = QTime.currentTime()
        displayHora = currentHora.toString('hh:mm')
        self.hora.setText(displayHora)
    
    def displayFecha(self):   
        currentFecha = QDate.currentDate()
        dia = currentFecha.toString('dddd')
        numero_dia = currentFecha.toString('dd')
        mes = currentFecha.toString('MMMM')
        anho = currentFecha.toString('yyyy')
        displayFecha = (dia + ', ' + numero_dia + ' de ' + mes + ' del ' + anho)
        self.fecha.setText(displayFecha)

    def actualizar(self):

        if self.estadoS1 == False:
            self.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            self.estadoS1=True
        else:
            self.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            self.estadoS1=False

        if self.estadoS2 == False:
            self.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
        if self.estadoS3 == False:
            self.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")

        
        



fecha_actual_list = ["viernes, 10 de junio del 2022","viernes, 10 de junio del 2020","viernes, 10 de junio del 2023"]
if __name__=='__main__':
    i=1
    estadoS1= True
    estadoS2= True
    estadoS3= True
    fecha_actual=fecha_actual_list[i]
    hora_actual="18:00 pm"
    temperatura_actual="21"
    app = QApplication(sys.argv)
    GUI = mirroll_GUI()
    GUI.show()
    sys.exit(app.exec_())



    # while True:
    #         fecha_actual=fecha_actual_list[i]
    #         i+=1            
    #         time.sleep(1)
    #         if i==3:
    #             i=0