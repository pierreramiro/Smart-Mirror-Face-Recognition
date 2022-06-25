import encodings
from quopri import encode
from MainWindow import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
import time

#Librería para el control del Raspberry
import RPi.GPIO as gpio
import serial #uart
gpio.setwarnings(False)

#Libreria para face recognition
import cv2
import face_recognition
import pickle
from imutils.video import VideoStream
import imutils

#Variables globales
rojo=[gpio.LOW,gpio.HIGH,gpio.LOW]
verde=[gpio.HIGH,gpio.LOW,gpio.LOW]
azul=[gpio.LOW,gpio.LOW,gpio.HIGH]
amarillo=[gpio.HIGH,gpio.HIGH,gpio.LOW]
cian=[gpio.HIGH,gpio.LOW,gpio.HIGH]
rosado=[gpio.LOW,gpio.HIGH,gpio.HIGH]
blanco=[gpio.HIGH,gpio.HIGH,gpio.HIGH]
colores=["rojo","verde","azul","amarillo","cian","rosado","blanco"]
coloresGPIO=[rojo,verde,azul,amarillo,cian,rosado,blanco]
#Face Recog resources
imagenesFaceRecognition = ['RostroIzq','RostroIzqMID','RostroFrente','RostroDerMID','RostroDer','RostroArriba']
imagenesProcessing=["Procesando1.png","Procesando2.png","Procesando3.png","Procesando4.png","Procesando5.png","Procesando6.png"]
#foldar names dataset
usersFolder=["user0","user1","user2","user3","user4","user5","user6","user7","user8","user9"]
#Cargamos el archivo precargado de los faces
knownEncodings = pickle.loads(open("encodings.pickle", "rb").read())


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
        self.layout=QtWidgets.QVBoxLayout()
        #Creo el texto a mostrar
        message = QtWidgets.QLabel("Se ha presionado el botón. Recibiendo información Bluetooth")
        self.layout.addWidget(message)
        #Creo la imagen
        image = QImage('resources/Bluetooth.jpeg')
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(self.imageLabel)
        #Configuramos/actualizamos el layout
        self.setLayout(self.layout)
        #Abrir puerto
        self.ser = serial.Serial ("/dev/ttyS0", 9600)    #Open port with baud rate
        #Creamos timer para sondear datos
        self.timer_Datos=QTimer()
        self.timer_Datos.timeout.connect(self.sondeaDatos)
        self.timer_Datos.start(300)

    def sondeaDatos(self):
        #recibir data:   [funcion,idUser,color,BINtomacorrientes,altura]
        received_data = self.ser.read()              #read serial port
        time.sleep(0.03)
        data_left = self.ser.inWaiting()             #check for remaining byte
        received_data += self.ser.read(data_left)
        if len(received_data)!=0:
            #Desactivamos sondeo, porque hemos recibido información. Lo activamos nuevamente al final
            #Esto lo hacemos para asegurar los tiempos entre timeouts
            self.timer_Datos.stop()
            #Decodificamos data
            print(received_data)
            received_data=eval(received_data.decode())
            #Con el primer elemento podemos revisar que función aplicamos
            if received_data[0]==0:
                """Trama de configurar rostro"""
                print("Al usuario: ",received_data[1],"Le modificaremos su rostro")
                #ponemos un popup de BT activado
                dlg = configureUser_DialogBox(self,idUser=received_data[1]-1) #Le restamos porque en la app están del 1 al 10
                dlg.show()

            elif received_data[0]==1:
                """Trama como usuario básico"""
                idUser=received_data[1]-1
                color=received_data[2]
                print("El usuario: ",idUser,"tiene color: ", color)
                parent=self.parent()
                #obtengo el usuario que se va a mostrar
                parent.IdUserToShow=idUser
                #Obtengo el Id del color a modificar
                parent.perfiles[idUser]=colores.index(color)

            elif received_data[0]==2:
                """Trama como admin"""
                idUser=received_data[1]-1
                color=received_data[2]
                BINtomacorrientes=str(received_data[3])
                altura=received_data[4]
                print("El usuario: ",idUser,"tiene color: ", color,"se activan:",BINtomacorrientes,"y altura:",altura)
                parent=self.parent()
                #obtengo el usuario que se va a mostrar
                parent.IdUserToShow=idUser
                #Obtengo el Id del color a modificar
                parent.perfiles[idUser][0]=altura
                parent.perfiles[idUser][1]=colores.index(color)
                parent.perfiles[idUser][2]=BINtomacorrientes

            elif received_data[0]==3:
                parent=self.parent()
                #activamos nuevamente el sondeo
                parent.waitingBT=1
                parent.timer_BT.start(5)
                #Cerramos aplicacion
                self.close()
            else:
                print("función no creada")
            #ACtivamos sondeo, que habiamos desactivado al inicio
            self.timer_Datos.start()
            
    #Esta función por si sola nos permite aceptar el evento de cierre (not modified)
    def closeEvent(self, event):
        self.timer_Datos.stop()
        event.accept()

class configureUser_DialogBox (QtWidgets.QDialog):
    def __init__(self,idUser=0):
        super().__init__()
        #Ponemos un nombre a la ventana3
        self.setWindowTitle("Reconocimiento Facial")
        self.setWindowIcon(QtGui.QIcon('resources/RFLogo.png'))
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
        self.idUser=idUser
        #Creamos unos widgets
        self.imageLabel = QtWidgets.QLabel()
        self.sencondLine = QtWidgets.QLabel("Coloque su rostro como muestra la imagen")   
        self.sencondLine.setStyleSheet("font: 21pt \"Arial Rounded MT Bold\";")
        self.sencondLine.setAlignment(QtCore.Qt.AlignCenter)
        #Agregamos un usuario
        self.addingNewUser()
        # #not neccessary
        # self.timer_Datos=QTimer()
        # self.timer_Datos.timeout.connect(self.cambiaImagen)
        # self.timer_Datos.start(200)
        
    def addingNewUser(self):
        frames=[]
        for i in range(18):
            faces=[]
            #Verificamos si hay cara en frente de la camara
            while len(faces)==0:
                #añadimos un delay
                time.sleep(0.1)
                #Tomamos una foto
                cam=cv2.VideoCapture(0)
                ret,frame=cam.read()
                cv2.imwrite("1.jpg",frame)
                cam.release()
                #Obtenemos la caras de la foto
                face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.1,4)
            
            if i!=0:
                #Se detecto una cara y Actualizamos el Dialog y colocamos el iconPhoto
                image=QImage('resources/CamP.png')
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.setLayout(self.layout)
                time.sleep(0.2)
                image=QImage('resources/'+imagenesFaceRecognition[i%6]+'.png')
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.setLayout(self.layout)
                #forzamos un delay
                time.sleep(1.5)
            else:
                #Esta es la primera vez
                self.layout.addWidget(self.sencondLine)
                image=QImage('resources/'+imagenesFaceRecognition[i%6]+'.png')
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.setLayout(self.layout)
                self.layout.addWidget(self.imageLabel)
                #forzamos un delay
                time.sleep(1.5)
            #Guardamos la foto para hacer procesamiento
            frames.append(frame)
        """Realizamos el procesamiento"""
        #De los frames guardados, hacemos el procesamiento        
        for i,frame in enumerate(frames):
            #Lo pasamos a rgb
            rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #detectamos los rostros boxes
            boxes = face_recognition.face_locations(rgb,model="hog") #Se escoge el modelo hog
            #obtenemos los encodings
            encodings = face_recognition.face_encodings(rgb, boxes)
            # loop over the encodings
            tempEncodings=[]
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                tempEncodings.append(encoding)
            #Reemplazamos por los datos que ya teníamos
            knownEncodings[self.idUser]=tempEncodings
            #Añadimos ventana de processing
            image=QImage('resources/'+imagenesProcessing[i%6]+'.png')
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.setLayout(self.layout)    
        #Cerramos ventana luego de realizar el procesamiento
        self.close()

    def cambiaImagen(self):#Ya no se usa
        self.j=self.j+1
        if self.i<0 and (self.j%15==0):
            self.sencondLine.setStyleSheet("font: 21pt \"Arial Rounded MT Bold\";")
            self.sencondLine.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.sencondLine)
            self.layout.addWidget(self.imageLabel)
            self.i=self.i+1

        if self.i<len(imagenesFaceRecognition) and self.i>=0 and (self.j%15==0):
            image=QImage('resources/'+imagenesFaceRecognition[self.i]+'.png')
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.setLayout(self.layout)
            self.i=self.i+1

        if (self.j%15)==13 and self.j>=28:
            image=QImage('resources/CamP.png')
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.setLayout(self.layout)
    
    def closeEvent(self, event):#Ya no se usa
        self.timer.stop()
        event.accept()

class mirrollGUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        #Creamos nuestra GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #Definimos 10 perfiles por defecto
        temp=[]
        for i in range(10):
            temp.append([0,1,"111"]) # guardamos los datos de los perfiles [altura,idColor,binData]
        self.perfiles=temp
        #Indicamos el usuario a mostrar su personalización
        self.IdUserToShow=0
        self.estadoS1= "1"==self.perfiles[self.IdUserToShow][2][0]
        self.estadoS2= "1"==self.perfiles[self.IdUserToShow][2][1]
        self.estadoS3= "1"==self.perfiles[self.IdUserToShow][2][2]
        #Establecemos info por defecto
        self.fecha_actual="viernes, 10 de junio del 2022"
        self.hora_actual="18:00 pm"
        self.temperatura_actual="21"
        self.ui.temperatura.setText(self.temperatura_actual)   
        #Creamos unas banderas
        self.SomeOneIsInFront=False
        #Creamos unas variables
        self.maxDistance= 150#maxima distancia en cm
        self.maxTimeEcho= self.maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO
        self.minDistance= 70#maxima distancia en cm
        self.minTimeEcho= self.minDistance*2/0.034
        #Configuramos los pines del Raspberry
        self.ConfigRaspberryGPIO()
        #Bajamos el espejo
        self.BajarEspejo()
        #Habilitamos para esperar conexion BT
        self.waitingBT=1
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



    """##################################"""
    """Establecemos los métodos/funciones"""
    """##################################"""
    def actualizar(self):
        #Chequeamos los estados
        self.estadoS1= "1"==self.perfiles[self.IdUserToShow][2][0]
        self.estadoS2= "1"==self.perfiles[self.IdUserToShow][2][1]
        self.estadoS3= "1"==self.perfiles[self.IdUserToShow][2][2]
        #Chequeamos el estado
        if self.estadoS1 == False:
            #Hacemos la impresion que se tiene ha soltado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            gpio.output(self.CH1pin,gpio.LOW)        
        else:
            #Hacemos la impresion que se tiene presionado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            gpio.output(self.CH1pin,gpio.HIGH)
        if self.estadoS2 == False:
            gpio.output(self.CH2pin,gpio.LOW)
            self.ui.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
        else:
            gpio.output(self.CH2pin,gpio.HIGH)
            self.ui.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            
        if self.estadoS3 == False:
            self.ui.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            gpio.output(self.CH3pin,gpio.LOW)
        else:
            gpio.output(self.CH3pin,gpio.HIGH)
            self.ui.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
        #actualizamos el color
        idColor=self.perfiles[self.IdUserToShow][1]
        gpio.output(self.LREDpin,coloresGPIO[idColor][0])
        gpio.output(self.LGREENpin,coloresGPIO[idColor][1])
        gpio.output(self.LBLUEpin,coloresGPIO[idColor][2])
    
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
        
        gpio.setup(21,gpio.OUT)
        gpio.output(21,gpio.HIGH)
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
        self.LGREENpin=23
        self.LBLUEpin=24
        #Configuramos como salidas
        gpio.setup(self.LREDpin,gpio.OUT)
        gpio.setup(self.LGREENpin,gpio.OUT)
        gpio.setup(self.LBLUEpin,gpio.OUT)
        #Configuramos todo en LOW
        gpio.output(self.LREDpin,gpio.LOW)
        gpio.output(self.LGREENpin,gpio.LOW)
        gpio.output(self.LBLUEpin,gpio.LOW)

        ######## ENTRADA BOTON #######
        self.BUTTONpin=25
        #Configuramos como entrada
        gpio.setup(self.BUTTONpin,gpio.IN,pull_up_down=gpio.PUD_UP)
        
        ######## SENSOR ULTRASONIDO #######
        ECHOpin=12
        TRIGpin=16
        #Configuramos como entrada
        gpio.setup(ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
        #Configuramos como salida
        gpio.setup(TRIGpin,gpio.OUT)
        gpio.output(TRIGpin,gpio.LOW)
        
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
        if gpio.input(self.BUTTONpin)==gpio.LOW and self.waitingBT==1:
            #Detenemos el sondeo
            self.timer_BT.stop()
            self.waitingBT=0
            #ponemos un popup de BT activado
            dlg = BT_DialogBox(self)
            dlg.show()
    
    def sondeoSensor(self):
        #medimos la distancia del sensor ultrasonido
        #tiempo de muestreo
        gpio.output(self.TRIGpin,gpio.HIGH)
        t1=time.time()
        #esperamos a cumplir los 10usec
        while time.time()<t1+0.00001: #nosotros esperamos hasta 10us
            pass
        gpio.output(self.TRIGpin,gpio.LOW)
        #Esperamos el echo en HIGH
        while not(gpio.input(self.ECHOpin)):
            #El echo tiene un timeout y se setea en baja
            pass
        t1=time.time()
        #Esperamos el echo en flanco de bajada
        while gpio.input(self.fECHOpin):
            pass
        runnningTime=(time.time()-t1)*1000000
        #Verificamos en que estado estamos
        if self.SomeOneIsInFront:
            #Esperamos que la persona en frente se haya ido. Para ello, el sensor debe medir mayor a 150cm
            if runnningTime>self.maxTimeEcho:
                print("Entramos en hinbernacion")
            #En caso la persona aún no se ha ido.. seguimos encendido mostrando la pantalla
        else:    
            #Verificamos los rangos para verificar si hay persona en frente
            if runnningTime<self.maxTimeEcho and runnningTime>self.minTimeEcho: 
                #Tenemos una persona en frente!
                self.SomeOneIsInFront=True
                print("distancia:",runnningTime*0.034/2)
                #Procedemos a verificar si hay rostro detectado
                #Verificamos si hay cara en frente de la camara
                vs = VideoStream(src=0,framerate=10).start()
                frame=vs.read()
                cv2.imwrite("1.jpg",frame)
                vs.stop()
                #Obtenemos la cara de la foto
                face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.1,4)
                if len(faces)!=0:
                    #Hay cara!
                    boxes = face_recognition.face_locations(frame)
                    frame = imutils.resize(frame, width=500)
                    # Detect the face boxes
                    boxes = face_recognition.face_locations(frame)
                    # compute the facial embeddings for each face bounding box
                    encodings = face_recognition.face_encodings(frame, boxes)
                    #definimos una variable para hallar que usuario tuvo mas match
                    idUserMatch=[0]*10
                    #De los encodings obtenidos (rostros calculados), verificamos con los conocidos
                    for encoding in encodings:
                        for id,dataEncs in enumerate(knownEncodings):
                            #Calculamos la cantidad de aciertos
                            matches=face_recognition.compare_faces(dataEncs,encoding)
                            #Sumamos la cantidad de aciertos
                            idUserMatch[id]+=matches.count(True) 
                    #En teoría, sea el caso que aparecieron mas rostros en la foto.. se escogerá el primero en orden    
                    self.IdUserToShow =idUserMatch.index(max(idUserMatch))
                    print(f"Usuario a mostrar: User{self.IdUserToShow+1}")
                #En caso no se haya detectado cara, no hacemos ninguna configuración. Se mantiene la anterior          

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


"""
Trama como admin(usuario) 
[funcion,id usuario,color,BINtomacorriente]
[2,3,rojo,101]

Trama como usuario básico
[funcion,id usuario,color]
[1,3,azul]

Trama configurar rostro
[funcion,id usuario]
[0,1]
"""