import encodings
from Control.Motor.controlMotor import BajarEspejo, SubirEspejo
from MainWindow import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
import time
import csv
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
noColor=[gpio.LOW,gpio.LOW,gpio.LOW]
rojo=[gpio.LOW,gpio.HIGH,gpio.LOW]
verde=[gpio.HIGH,gpio.LOW,gpio.LOW]
azul=[gpio.LOW,gpio.LOW,gpio.HIGH]
amarillo=[gpio.HIGH,gpio.HIGH,gpio.LOW]
cian=[gpio.HIGH,gpio.LOW,gpio.HIGH]
rosado=[gpio.LOW,gpio.HIGH,gpio.HIGH]
blanco=[gpio.HIGH,gpio.HIGH,gpio.HIGH]
colores=["noColor","rojo","verde","azul","amarillo","cian","rosado","blanco"]
coloresGPIO=[noColor,rojo,verde,azul,amarillo,cian,rosado,blanco]
#Face Recog resources
imagenesFaceRecognition = ['RostroIzq','RostroIzqMID','RostroFrente','RostroDerMID','RostroDer','RostroArriba']
imagenesProcessing=["Procesando1.png","Procesando2.png","Procesando3.png","Procesando4.png","Procesando5.png","Procesando6.png"]
#foldar names dataset
usersFolder=["user0","user1","user2","user3","user4","user5","user6","user7","user8","user9"]
#Cargamos el archivo precargado de los faces
knownEncodings = pickle.loads(open("encodings.pickle", "rb").read())
#variables globales
STEPTIME=125/2*1000#en nanosec
pulsesPerRev=0#200
distPerRev=1
PULSES_PER_DIST=pulsesPerRev/distPerRev
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
        #Flag
        self.ConfigRostro=False
        self.CloseWindow=False
        #Creamos timer para sondear datos
        self.timer_Datos=QTimer()
        self.timer_Datos.timeout.connect(self.sondeaDatos)
        self.timer_Datos.start(300)

    def sondeaDatos(self):
        if self.ConfigRostro:
            return
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
                temp=received_data[1]-1
                parent=self.parent()
                self.ConfigRostro=True
                dlg = configureUser_DialogBox(parent,self,temp) #Le restamos porque en la app están del 1 al 10
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
                #activamos los actuadores
                parent.configureGPIOMirrol()

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
                #activamos los actuadores
                parent.configureGPIOMirrol()

            elif received_data[0]==3:
                #Cerramos aplicacion
                #Guardamos los nuevos perfiles en un csv
                file=open("userConfig.csv","w")
                writer=csv.writer(file)
                parent=self.parent()
                perfiles=parent.perfiles
                for row in perfiles[0:-1]:
                    writer.writerow(row)
                file.close()
                self.close()
            else:
                print("función no creada")
            #Activamos sondeo, que habiamos desactivado al inicio
            if not(self.CloseWindow):
                self.timer_Datos.start()
            
    #Esta función por si sola nos permite aceptar el evento de cierre (not modified)
    def closeEvent(self, event):
        parent=self.parent()
        #activamos nuevamente el sondeo
        parent.timer_display.start(500)
        parent.timer_activeUser.start(100)
        self.CloseWindow=True
        print("Salimos del BT mode")
        event.accept()

class configureUser_DialogBox (QtWidgets.QDialog):
    def __init__(self,parent=None,child=None,idUser=0):
        super(configureUser_DialogBox,self).__init__(parent)
        self.child=child
        #añadimos flag
        parent.AddingNewUser=True
        #Ponemos un nombre a la ventana3
        self.setWindowTitle("Reconocimiento Facial")
        self.setWindowIcon(QtGui.QIcon('resources/RFLogo.png'))
        self.resize(600, 600)
        #creo el layout de nuestra ventana (vertical)
        self.layout=QtWidgets.QVBoxLayout()
        #Creo el texto a mostrar
        self.message = QtWidgets.QLabel("Acérquese a la cámara")
        self.message.setStyleSheet("font: 16pt \"Arial Rounded MT Bold\";")
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.message)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)
        #seteando variables
        self.idUser=idUser
        self.frames=[]
        self.countPics=0
        self.picTaken=False
        self.ponerNuevaPose=True
        self.maxNumbersPics=6
        #Creamos unos widgets
        self.imageLabel = QtWidgets.QLabel()
        self.sencondLine = QtWidgets.QLabel("Coloque su rostro como muestra la imagen")   
        self.sencondLine.setStyleSheet("font: 21pt \"Arial Rounded MT Bold\";")
        self.sencondLine.setAlignment(QtCore.Qt.AlignCenter)
        #Configuramos los timers
        self.timer_one=QTimer()
        self.timer_one.timeout.connect(self.takePicsNewUser)
        self.timer_two=QTimer()
        self.timer_two.timeout.connect(self.processPicsNewUser)
        #Iniciamos los timer
        self.timer_one.start(800)
        print("Salimos del init FR")
        
    def takePicsNewUser(self):
        print("Tomamos foto")
        if self.countPics==self.maxNumbersPics:
            #Detenenmos este timer
            self.timer_one.stop()
            #resetamos esta variable para el sgte timer
            self.countPics=0
            #Inicializamos el evento de processing
            self.timer_two.start(800)
        if self.picTaken:
            #Colocamos la actualizacion de imágenes
            if self.countPics!=0:
                if not(self.ponerNuevaPose):
                    #Pedimos al usuario una nueva pose
                    time.sleep(0.5)
                    image=QImage('resources/'+imagenesFaceRecognition[self.countPics%6]+'.png')
                    self.imageLabel.setPixmap(QPixmap.fromImage(image))
                    self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                    self.setLayout(self.layout)
                    self.ponerNuevaPose=True
                    #Seteamos los flags, pedimos una foto nueva y ya tenemos foto guardada
                    self.picTaken=False
                    self.countPics+=1
                else:
                    #Efecto de que se tomo una foto
                    image=QImage('resources/CamP.png')
                    self.imageLabel.setPixmap(QPixmap.fromImage(image))
                    self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                    self.setLayout(self.layout)#añadimos la imagen
                    self.ponerNuevaPose=False
            else:
                #Esta es la primera vez
                image=QImage('resources/'+imagenesFaceRecognition[self.countPics%6]+'.png')
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.layout.addWidget(self.sencondLine)
                self.layout.addWidget(self.imageLabel)
                self.setLayout(self.layout)
                self.show()
                self.picTaken=False
                self.countPics+=1
        else:
            faces=[]
            #Verificamos si hay cara en frente de la camara
            while len(faces)==0 and not(self.picTaken):
                # #añadimos un delay
                # time.sleep(0.1)
                #Tomamos una foto
                cam=cv2.VideoCapture(0)
                ret,frame=cam.read()
                cv2.imwrite("1.jpg",frame)
                cam.release()
                #Obtenemos la caras de la foto
                face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.1,4)
            self.picTaken=True
            print("foto: ",self.countPics)
            #Guardamos la foto para hacer procesamiento
            self.frames.append(frame)
        
    def processPicsNewUser(self):
        print("procesamos foto")
        if self.countPics==self.maxNumbersPics:
            #desahibiltamos el timer
            self.timer_two.stop()
            #Guardamos el nuevo pickle
            f = open("encodings.pickle", "wb")
            f.write(pickle.dumps(knownEncodings))
            f.close()
            #Cerramos la ventana
            self.close()
        """Realizamos el procesamiento"""
        frame=self.frames[self.countPics]
        #Lo pasamos a rgb
        rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #Guardamos la imagen
        cv2.imwrite("dataset/User"+str(self.idUser)+"/image"+str(self.countPics)+".png",frame)
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
        image=QImage('resources/'+imagenesProcessing[self.countPics%6])
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.setLayout(self.layout)    
        #aumentamos el contador
        self.countPics+=1
    
    def closeEvent(self, event):#Ya no se usa
        self.child.ConfigRostro=False
        event.accept()

class mirrollGUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        #Creamos nuestra GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #Cargamos el archivo guardado con la configuracion de los perfiles
        file=open("userConfig.csv","r")
        reader=csv.reader(file)
        temp=[]
        for row in reader:
            temp.append([float(row[0]),int(row[1]),row[2]]) # formato [altura,idColor,binData]
        file.close()
        #Definimos el perfil 10 por defecto
        temp.append([30,7,"001"])
        self.perfiles=temp
        #Indicamos el usuario a mostrar y su personalización
        self.IdUserToShow=10#por defecto
        self.estadoS1= "1"==self.perfiles[self.IdUserToShow][2][0]
        self.estadoS2= "1"==self.perfiles[self.IdUserToShow][2][1]
        self.estadoS3= "1"==self.perfiles[self.IdUserToShow][2][2]
        #Establecemos info por defecto
        self.fecha_actual="viernes, 10 de junio del 2022"
        self.hora_actual="18:00 pm"
        self.temperatura_actual="21"
        self.ui.temperatura.setText(self.temperatura_actual)   
        #Creamos unas variables flags
        self.initFlag=True
        #Definimos unas variables
        self.maxDistance= 60#maxima distancia en cm
        self.maxTimeEcho= self.maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO en us
        self.minDistance= 30#maxima distancia en cm
        self.minTimeEcho= self.minDistance*2/0.034 #en usec
        self.STEPTIME=STEPTIME_motor #En microsegundos
        self.actualAltura=30
        #Configuramos los pines del Raspberry
        self.ConfigRaspberryGPIO()
        
        """Creamos distintos timer que realizarán un sondeo (Poll), actualizarán datos, checar{a el sleep entre otros"""
        #Timer para inicio de Mirroll
        self.timer_initMirroll= QTimer(self)
        self.timer_initMirroll.timeout.connect(self.initMirror)
        self.timer_initMirroll.start(800)
        #Creamos el timer para sondear presencia de usuarios
        self.timer_sondeaPresencia=QTimer(self)
        self.timer_sondeaPresencia.timeout.connect(self.sondeaPresencia)
        #Creamos el timer cuando se tiene un usuario activo
        self.timer_activeUser=QTimer(self)
        self.timer_activeUser.timeout.connect(self.stillThere)
        #Timer que actualiza los display de la GUI cuando se tiene al usuario activo
        self.timer_display=QTimer(self)
        self.timer_display.timeout.connect(self.displayFecha)
        self.timer_display.timeout.connect(self.displayHora) 
        self.timer_GPIO=QTimer(self)
        self.timer_GPIO.timeout.connect(self.configureGPIOMirrol)       

    """##################################"""
    """Establecemos los métodos/funciones"""
    """##################################"""
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
        """Ojo, el pin 5 no tiene pullup.. asi que usamos el pin3 como una fuente de 3.3v"""
        gpio.setup(3,gpio.OUT)
        gpio.output(3,gpio.HIGH)
        self.LSUPpin=5
        self.LSDOWNpin=6
        #Configuramos como entradas
        gpio.setup(self.LSUPpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
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
        self.ECHOpin=12
        self.TRIGpin=16
        #Configuramos como entrada
        gpio.setup(self.ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
        #Configuramos como salida
        gpio.setup(self.TRIGpin,gpio.OUT)
        gpio.output(self.TRIGpin,gpio.LOW)

    def initMirror(self):
        if self.initFlag:
            """Colocamos una imagen o algo de bienvenida.. un layout"""
            self.initFlag=False
        else:
            self.timer_initMirroll.stop()
            self.SubirEspejo()
            print("Limit activado!")
            #Procedemos a entrar al modo sleep!
            self.setSleepMirrolMode()
            #Empezamos a sondear presencia
            self.timer_sondeaPresencia.start(1000)   

    def sondeaPresencia(self):
        #medimos la distancia del sensor ultrasonido
        #tiempo de muestreo
        gpio.output(self.TRIGpin,gpio.HIGH)
        t1=time.time()
        #esperamos a cumplir los 10usec
        while time.time()<t1+0.00001: #nosotros esperamos hasta 10us
            pass
        gpio.output(self.TRIGpin,gpio.LOW)
        #Esperamos el echo en HIGH o su timeout
        t_timeout=time.time()+0.020
        while not(gpio.input(self.ECHOpin)):
            #establecemos un timeout de 20ms
            if time.time()>t_timeout:
                break
        t1=time.time()
        #Esperamos el echo en flanco de bajada
        t_timeout=time.time()+self.maxTimeEcho*1.2
        while gpio.input(self.ECHOpin):
            #establecemos un timeout de 1.2 veces el máximo aceptado
            if time.time()>t_timeout:
                break
        runnningTime=(time.time()-t1)*1000000
        #Verificamos los rangos para verificar si hay persona en frente
        if runnningTime<self.maxTimeEcho: 
            #Tenemos una persona en frente!. Prendemos luces en blanco
            self.setColorLeds("blanco")
            #Verificamos rostro con camara..
            print("distancia:",runnningTime*0.034/2)
            #Procedemos a verificar si hay rostro detectado
            vs = VideoStream(src=0,framerate=10).start()
            frame=vs.read()
            cv2.imwrite("1.jpg",frame)
            vs.stop()
            #Obtenemos la cara de la foto
            face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces=face_cascade.detectMultiScale(gray,1.1,4)
            if len(faces)!=0:
                #Hay cara! será conocida o desconocidad???
                #Salimos del modo sleep
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
                #Verificamos si no hubo un match
                if idUserMatch==[0]*10:
                    #Configuración por defecto
                    self.IdUserToShow=10
                    self.configureGPIOMirrol()
                    self.IdUserToShow =10                    
                    print(f"Usuario Desconocido")
                    
                else:
                    #Configuracion personalizada
                    #En teoría, sea el caso que aparecieron mas rostros en la foto.. se escogerá el primero en orden    
                    self.IdUserToShow =idUserMatch.index(max(idUserMatch))
                    print(f"Usuario a mostrar: User{self.IdUserToShow+1}")
                    self.configureGPIOMirrol()
                #Detenemos este timer y habilitamos otro que actualizara Fecha, hora, botón, BT, entre otros
                self.timer_sondeaPresencia.stop()
                self.timer_display.start(500)
                self.timer_activeUser.start(100)
            #En caso no se haya detectado cara, no hacemos ninguna configuración. 
            #Seguimos en hibernacion.. probando
        else:
            self.setColorLeds("noColor")

    def stillThere(self):
        #Verificamos el boton
        if gpio.input(self.BUTTONpin)==False:
            #Detenemos el sondeo
            print("Button pressed")
            self.timer_activeUser.stop()
            #ponemos un popup de BT activado
            dlg = BT_DialogBox(self)
            dlg.show()
        else:
            gpio.output(self.TRIGpin,gpio.HIGH)
            t1=time.time()
            #esperamos a cumplir los 10usec
            while time.time()<t1+0.00001: #nosotros esperamos hasta 10us
                pass
            gpio.output(self.TRIGpin,gpio.LOW)
            #Esperamos el echo en HIGH
            t_timeout=time.time()+0.020
            while not(gpio.input(self.ECHOpin)):
                #establecemos un timeout de 20ms
                if time.time()>t_timeout:
                    break
            t1=time.time()
            #Esperamos el echo en flanco de bajada
            t_timeout=time.time()+self.maxTimeEcho*1.2
            while gpio.input(self.ECHOpin):
                #establecemos un timeout de 1.2 veces el máximo aceptado
                if time.time()>t_timeout:
                    break
            runnningTime=(time.time()-t1)*1000000
            if runnningTime>self.maxTimeEcho:
                print("Sensor, no detecta. Verificamos nuevamente y con camara")
                #Ya no hay persona al frente. Pero verificamos nuevamente
                """Calculamos nuevamente con el sensor"""
                time.sleep(1)
                gpio.output(self.TRIGpin,gpio.HIGH)
                t1=time.time()
                #esperamos a cumplir los 10usec
                while time.time()<t1+0.00001: #nosotros esperamos hasta 10us
                    pass
                gpio.output(self.TRIGpin,gpio.LOW)
                #Esperamos el echo en HIGH
                t_timeout=time.time()+0.020
                while not(gpio.input(self.ECHOpin)):
                    #establecemos un timeout de 20ms
                    if time.time()>t_timeout:
                        break
                t1=time.time()
                #Esperamos el echo en flanco de bajada
                t_timeout=time.time()+self.maxTimeEcho*1.2
                while gpio.input(self.ECHOpin):
                    #establecemos un timeout de 1.2 veces el máximo aceptado
                    if time.time()>t_timeout:
                        break
                runnningTime=(time.time()-t1)*1000000
                """Calculemos con la camara"""
                #Procedemos a verificar si hay rostro detectado
                vs = VideoStream(src=0,framerate=10).start()
                frame=vs.read()
                #cv2.imwrite("1.jpg",frame)
                vs.stop()
                #Obtenemos la cara de la foto
                face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.1,4)
                if runnningTime>self.maxTimeEcho and len(faces)==0:
                    #Si esta vez no se vuelve a detectar a nadie.. Entramos en modo sleep
                    #activamos nuevamente el timer adecuado y apagamos los actuales
                    print("No hay nadie")
                    self.timer_activeUser.stop()
                    self.timer_display.stop()
                    self.setSleepMirrolMode()
                    self.timer_sondeaPresencia.start(1000)
    
    def displayFecha(self):
        """Fecha"""
        currentFecha = QDate.currentDate()
        dia = currentFecha.toString('dddd')
        numero_dia = currentFecha.toString('dd')
        mes = currentFecha.toString('MMMM')
        anho = currentFecha.toString('yyyy')
        displayFecha = (dia + ', ' + numero_dia + ' de ' + mes + ' del ' + anho)
        self.ui.fecha.setText(displayFecha)
    
    def displayHora(self):
        """Hora"""
        currentHora = QTime.currentTime()
        displayHora = currentHora.toString('hh:mm')
        self.ui.hora.setText(displayHora)

    def configureGPIOMirrol(self):
        """Relés"""
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
        """Color"""
        idColor=self.perfiles[self.IdUserToShow][1]
        gpio.output(self.LREDpin,coloresGPIO[idColor][0])
        gpio.output(self.LGREENpin,coloresGPIO[idColor][1])
        gpio.output(self.LBLUEpin,coloresGPIO[idColor][2])
        """Altura motor"""
        diffAltura=self.perfiles[self.IdUserToShow][0]-self.actualAltura
        if diffAltura<0:
            #Bajamos motor
            print("bajamos motor")
            diffAltura=abs(diffAltura)
            #BajarEspejo(diffAltura)
        elif diffAltura>0:
            #Subimos motor
            print("subimos motor")
            #SubirEspejo(diffAltura)
        else:
            #mantenemos la altura
            print("Dejamos la altura")
        self.actualAltura=self.perfiles[self.IdUserToShow][0]


    def setColorLeds(self,color):
        #actualizamos el color
        idColor=colores.index(color)
        #Definimos los canales
        gpio.output(self.LREDpin,coloresGPIO[idColor][0])
        gpio.output(self.LGREENpin,coloresGPIO[idColor][1])
        gpio.output(self.LBLUEpin,coloresGPIO[idColor][2])
    
    def setSleepMirrolMode(self):
        self.setColorLeds("noColor")
        gpio.output(self.CH1pin,gpio.LOW)
        gpio.output(self.CH2pin,gpio.LOW)
        gpio.output(self.CH3pin,gpio.LOW)
        self.SubirEspejo()
   
    def BajarEspejo(self,distancia=-1): 
        #Habilitamos el driver del motor
        gpio.output(self.ENApin,gpio.LOW)
        #Definimos la dirección
        gpio.output(self.DIRpin,gpio.LOW)
        if distancia==-1:
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
            #Bajamos una cierta altura o hasta sentir el Limit switch
            for i in range(distancia*PULSES_PER_DIST):
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    if gpio.input(self.LSDOWNpin)==0:
                        break
                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    if gpio.input(self.LSDOWNpin)==0:
                        break
        gpio.output(self.ENApin,gpio.HIGH)
    
    def SubirEspejo(self,distancia=-1): 
        #Habilitamos el driver del motor
        gpio.output(self.ENApin,gpio.LOW)
        #Definimos la dirección
        gpio.output(self.DIRpin,gpio.HIGH)
        if distancia==-1:
            #Subimos el espejo hasta sentir el limit switch
            while gpio.input(self.LSUPpin)==0:#notar que se detiene en flanco de subida!
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
            #Subimos el espejo una cierta altura o hasta sentir el limit switch
            for i in range(distancia*PULSES_PER_DIST):
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    if gpio.input(self.LSUPpin)!=0:
                        break
                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<STEPTIME:
                    if gpio.input(self.LSUPpin)!=0:
                        break
        #Deshabilitamos el driver del motor
        gpio.output(self.ENApin,gpio.HIGH)

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