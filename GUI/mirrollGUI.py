from MainWindow import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QDate
import time


""" //////////////////////////////////////////
    //               Clases                 //
    //////////////////////////////////////////
""" 
class mirrollGUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        #Creamos nuestra GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Definimos unas variables globales
        self.estadoS1= True
        self.estadoS2= True
        self.estadoS3= True
        self.fecha_actual="viernes, 10 de junio del 2022"
        self.hora_actual="18:00 pm"
        self.temperatura_actual="21"
        self.ui.temperatura.setText(self.temperatura_actual)        
        #Creamos un timer
        self.timer = QTimer(self)
        #Hacemos la connect de los eventos
        self.setUpConnect()
        #Iniciamos el timer
        self.timer.start(1000)

    """######################"""
    """Conectamos los eventos"""
    """######################"""
    def setUpConnect(self):
        self.timer.timeout.connect(self.displayFecha)
        self.timer.timeout.connect(self.displayHora)
        self.timer.timeout.connect(self.actualizar)

    """########################"""
    """Establecemos los métodos"""
    """########################"""
    def actualizar(self):
        if self.estadoS1 == False:
            #Hacemos la impresion que se tiene ha soltado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            self.estadoS1=True
        else:
            #Hacemos la impresion que se tiene presionado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            self.estadoS1=False
        if self.estadoS2 == False:
            self.ui.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
        if self.estadoS3 == False:
            self.ui.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
    
    def displayFecha(self):   
        currentFecha = QDate.currentDate()
        dia = currentFecha.toString('dddd')
        numero_dia = currentFecha.toString('dd')
        mes = currentFecha.toString('MMMM')
        anho = currentFecha.toString('yyyy')
        displayFecha = (dia + ', ' + numero_dia + ' de ' + mes + ' del ' + anho)
        self.ui.fecha.setText(displayFecha)
    
    def displayHora(self):
        currentHora = QTime.currentTime()
        displayHora = currentHora.toString('hh:mm')
        self.ui.hora.setText(displayHora)


""" //////////////////////////////////////////
    //                Main                  //
    //////////////////////////////////////////
""" 
def setUpMirrollGUI():

    #Creamos la app
    app = QtWidgets.QApplication(sys.argv)  
    #Creamos el visualizador, solo la pantalla
    mirrolGUI_window=mirrollGUI()
    mirrolGUI_window.show()                        
    sys.exit(app.exec_())