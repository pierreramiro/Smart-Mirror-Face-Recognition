from MainWindow import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QDate, 
from PyQt5.QtGui import QImage,QPixmap
import time

#Librería para el control del Raspberry
import RPi.GPIO as gpio
import serial #uart

""" //////////////////////////////////////////
    //               Clases                 //
    //////////////////////////////////////////
""" 
class BT_DialogBox (QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(BT_DialogBox,self).__init__(parent)
        #Ponemos un nombre a la ventana
        self.setWindowTitle("Notificación")
        #creo el layout de nuestra ventana (vertical)
        self.layout=QtWidgets.QVBoxLayout 
        #Creo el texto a mostrar
        message = QtWidgets.QLabel("Se ha presionado el botón. Recibiendo información Bluetooth")
        self.layout.addWidget(message)
        #Creo la imagen
        image = QImage('resources/Bluetooth.png')
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(self.imageLabel)
        #Configuramos el layout
        self.setLayout(self.layout)

        self.timer=QTimer()
        self.timer.timeout.connect(self.CloseWarning)
        self.timer.start(1000)
        
    def CloseWarning(self):
        print("cerrando")
        self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


class NewUser_DialogBox (QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(NewUser_DialogBox,self).__init__(parent)
        self.setWindowTitle("HELLO!")
        self.timer=QTimer()
        self.timer.timeout.connect(self.CloseWarning)
        self.timer.start(1000)
        
    def CloseWarning(self):
        print("cerrando")
        self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

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
        #Configuramos los pines del Raspberry
        self.ConfigRaspberryGPIO()
        #Bajamos el espejo
        self.BajarEspejo()
        #Hacemos la connect de los eventos
        self.setUpConnect()
        """Creamos distintos timer que realizarán un sondeo (Poll) y actualizarán datos"""
        #Timer para actualizar los PARAMETROS DE LA INTERFAZ
        self.timer_Params = QTimer(self)
        self.timer_Params.timeout.connect(self.displayFecha)
        self.timer_Params.timeout.connect(self.displayHora)
        self.timer_Params.timeout.connect(self.actualizar)
        self.timer_Params.start(500)
        #Timer para escuchar al BLUETOOTH
        self.timer_BT = QTimer(self)
        self.timer_BT.timeout.connect(self.sondeoBT)
        self.timer_BT.start(5)
        
        #Timer para escuchar al SENSOR ULTRASONIDO
        self.timer_HCSR = QTimer(self)


    """########################"""
    """Establecemos los métodos/funciones"""
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

    def ConfigRaspberryGPIO(self):
        #Elegimos el modo de la numeración del chip BCM
        gpio.setmode(gpio.BCM)
        """Definimos la funcion de cada GPIO pin (in,out,serial,i2c,pwm,etc)"""
        ######## CONTROL MOTOR #######
        self.ENApin=17
        self.DIRpin=27
        self.PULpin=22
        #Configuramos como salidas
        gpio.setup(self.ENApin,gpio.OUT)
        gpio.setup(self.DIRpin,gpio.OUT)
        gpio.setup(self.PULpin,gpio.OUT)
        #Configuramos todo en LOW
        gpio.output(self.ENApin,gpio.HIGH)
        gpio.output(self.DIRpin,gpio.LOW)
        gpio.output(self.PULpin,gpio.LOW)
        
        ######## CONTROL CARGAS #######
        self.CH1pin=10
        self.CH2pin=9     
        self.CH3pin=11
        #Configuramos como salidas
        gpio.setup(self.CH1pin,gpio.OUT)
        gpio.setup(self.CH2pin,gpio.OUT)
        gpio.setup(self.CH3pin,gpio.OUT)
        #Configuramos todo en LOW
        gpio.output(self.CH1pin,gpio.LOW)
        gpio.output(self.CH2pin,gpio.LOW)
        gpio.output(self.CH3pin,gpio.LOW)
        
        ######## ENTRADAS LIMITS SWITCH #######
        self.LSUPpin=5
        self.LSDOWNpin=6
        #Configuramos como entradas
        gpio.setup(self.LSUPpin,gpio.IN,pull_up_down=gpio.PUD_UP)
        gpio.setup(self.LSDOWNpin,gpio.IN,pull_up_down=gpio.PUD_UP)

        ######## BLUETOOTH #######
        ser = serial.Serial ("/dev/ttyS0", 9600)    #Open port with baud rate

        ######## CONTROL LUCES #######
        self.LREDpin=18
        self.LREDpin=23
        self.LREDpin=24
        #Configuramos como salidas
        gpio.setup(self.LREDpin,gpio.OUT)
        gpio.setup(self.LREDpin,gpio.OUT)
        gpio.setup(self.LREDpin,gpio.OUT)
        #Configuramos todo en LOW
        gpio.output(self.LREDpin,gpio.LOW)
        gpio.output(self.LREDpin,gpio.LOW)
        gpio.output(self.LREDpin,gpio.LOW)

        ######## ENTRADA BOTON #######
        self.BUTTONpin=25
        #Configuramos como entrada
        gpio.setup(self.BUTTONpin,gpio.IN,pull_up_down=gpio.PUD_UP)
        
        ######## SENSOR ULTRASONIDO #######
        #Trigger pin
        self.TRIGpin=16
        gpio.setup(self.TRIGpin,gpio.OUT)
        gpio.output(self.LREDpin,gpio.LOW)
        #Echo pin
        self.ECHOpin=12
        gpio.setup(self.ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
        
    def BajarEspejo(self,altura=-1,STEPTIME=125/2*1000): #STEPTIME debe estar en nanosecs
        #Habilitamos el driver del motor
        gpio.output(self.ENApin,gpio.LOW)
        #Definimos la dirección
        gpio.output(self.DIRpin,gpio.HIGH)
        if altura==-1:
            #Bajamos el espejo hasta sentir el limit switch
            while gpio.input(self.LSDOWNpin)!=0:
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    pass

                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    pass
        else:
            #Bajamos una cierta altura
            """Es similar al anterior, solo que en vez de un while para checar el limit, se le añade la distanciaa estimada por calculo del factor de pulsos/m"""
        #Deshabilitamos el driver del motor
        gpio.output(self.ENApin,gpio.HIGH)

    def sondeoBT(self):
        """analizamos si se tiene presionó el botón"""
        if gpio.input(self.BUTTONpin)==gpio.LOW:
            #ponemos un popup de Botón presionado
            dlg = warningBox(self)
            dlg.show()


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