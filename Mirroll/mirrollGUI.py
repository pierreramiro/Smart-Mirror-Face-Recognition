from MainWindow import Ui_MainWindow
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
PATH_REPO='/home/smartmirror/Documents/Github/Smart-Mirror-Face-Recognition'

""" //////////////////////////////////////////
    //               Clases                 //
    //////////////////////////////////////////
""" 
class sleepModeDialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(sleepModeDialog,self).__init__(parent)
        # Desaparecemos el titleBar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        # Establecemos el tamaño de la pantalla
        self.setGeometry(0,0, WIDTH_SCREEN, HEIGHT_SCREEN)
        # Establecemos el fondo de color negro
        self.setStyleSheet("background:black")
        # Creo un layout
        self.layout = QtWidgets.QVBoxLayout()
        # loading image
        image = QImage('resources/RFLogo.png')
        image=image.scaled(int(WIDTH_SCREEN/3), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)
        # Configuramos el layout
        self.setLayout(self.layout)
        # Establecemos un timer para ejecutarse una vez
        self.timer_init=QTimer()
        self.timer_init.timeout.connect(self.setMirroll)
        self.timer_init.start(1000)
        self.timer_sondeaPresencia=QTimer()
        self.timer_sondeaPresencia.timeout.connect(self.sondeaPresencia)
        self.countTimesSondeo=0

    def setMirroll(self):
        #detenemos el timer
        self.timer_init.stop()
        #Hacemos el procesamiento y la configuración
        if self.parent().initialization:
            self.parent().initialization=False
            #Hacemos un pull para actualizar algunas variables del código
            from git import Repo
            repo = Repo(PATH_REPO)
            origin = repo.remote(name='origin')
            origin.pull()        
            #Cargamos el enntrenamiento
            self.parent().knownEncodings = pickle.loads(open("encodings.pickle", "rb").read())
            #Cargamos el archivo guardado con la configuracion de los perfiles
            file=open("userConfig.csv","r")
            reader=csv.reader(file)
            temp=[]
            for row in reader:
                if float(row[0])>MAXIMA_ALTURA_ESPEJO:
                    temp.append([MAXIMA_ALTURA_ESPEJO,int(row[1]),row[2]]) # formato [altura,idColor,binData]
                else:
                    temp.append([float(row[0]),int(row[1]),row[2]]) # formato [altura,idColor,binData]
            file.close()
            #Definimos el perfil 10 que será el usuario por defecto (no tiene configuracion)
            temp.append([MAXIMA_ALTURA_ESPEJO,7,"001"])
            self.parent().perfiles=temp
            #Indicamos el usuario a mostrar y su personalización
            self.parent().IdUserToShow=10#por defecto
            self.parent().estadoS1= "1"==self.parent().perfiles[self.parent().IdUserToShow][2][0]
            self.parent().estadoS2= "1"==self.parent().perfiles[self.parent().IdUserToShow][2][1]
            self.parent().estadoS3= "1"==self.parent().perfiles[self.parent().IdUserToShow][2][2]
            #Configuramos los pines del Raspberry
            self.parent().ConfigRaspberryGPIO()
        #Volvemos a establecer el espejo al tope
        self.parent().SubirEspejo()
        #print("Limit activado!")
        #Procedemos a entrar al modo sleep!
        self.parent().setColorLeds("noColor")
        gpio.output(self.parent().CH1pin,gpio.HIGH)
        gpio.output(self.parent().CH2pin,gpio.HIGH)
        gpio.output(self.parent().CH3pin,gpio.HIGH)
        self.parent().actualAltura=MAXIMA_ALTURA_ESPEJO
        self.parent().SubirEspejo()
        #Empezamos a sondear presencia
        self.timer_sondeaPresencia.start(500) 

    def sondeaPresencia(self):
        #medimos la distancia del sensor ultrasonido
        #tiempo de muestreo
        gpio.output(self.parent().TRIGpin,gpio.HIGH)
        t1=time.time()
        #esperamos a cumplir los 10usec
        while time.time()<t1+0.00001: #nosotros esperamos hasta 10us
            pass
        gpio.output(self.parent().TRIGpin,gpio.LOW)
        #Esperamos el echo en HIGH o su timeout
        t_timeout=time.time()+0.020
        while not(gpio.input(self.parent().ECHOpin)):
            #establecemos un timeout de 20ms
            if time.time()>t_timeout:
                break
        t1=time.time()
        #Esperamos el echo en flanco de bajada
        t_timeout=time.time()+self.parent().maxTimeEcho*1.2
        while gpio.input(self.parent().ECHOpin):
            #establecemos un timeout de 1.2 veces el máximo aceptado
            if time.time()>t_timeout:
                break
        runnningTime=(time.time()-t1)*1000000
        #Verificamos los rangos para verificar si hay persona en frente
        if runnningTime<self.parent().maxTimeEcho: 
            #Tenemos algo en frente!. Prendemos luces en blanco.
            self.parent().setColorLeds("blanco")
            #print("distancia:",runnningTime*0.034/2)
            #Verificamos rostro con camara y verificaremos N veces..
            N_triesOfVerification=1
            nPhotosTaken=0
            idUserDetected=[]
            exitSleepMode=True
            cam = cv2.VideoCapture(0)
            #vs = VideoStream(src=0,framerate=10).start()
            face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            while nPhotosTaken<N_triesOfVerification:
                # Sumamos la cantidad de veces que hemos tomado la foto
                nPhotosTaken+=3
                # Tomamos la photo
                ret, frame = cam.read()
                #cv2.imwrite(str(nPhotosTaken)+".jpg",frame)
                # Obtenemos la cara de la foto
                #print("Fotos tomadas",nPhotosTaken)
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.1,4)
                # Procedemos a verificar si hay rostro o no
                if len(faces)!=0:
                    #Hay cara! será conocida o desconocidad???
                    #boxes = face_recognition.face_locations(frame)
                    frame = imResize(frame, width=500)
                    # Detect the face boxes
                    boxes = FR_face_locations(frame)
                    # compute the facial embeddings for each face bounding box
                    encodings = FR_face_encodings(frame, boxes)
                    #definimos una variable para hallar que usuario tuvo mas match
                    idUserMatch=[0]*10
                    #De los encodings obtenidos (rostros calculados), verificamos con los conocidos
                    for encoding in encodings:
                        for id,dataEncs in enumerate(self.parent().knownEncodings):
                            #Calculamos la cantidad de aciertos
                            matches=FR_compare_faces(dataEncs,encoding)
                            #Sumamos la cantidad de aciertos
                            idUserMatch[id]+=matches.count(True) 
                    #Verificamos si no hubo un match
                    if idUserMatch==[0]*10:
                        #Configuración por defecto
                        idUserDetected.append(10)
                        #print(f"Usuario Desconocido")                        
                    else:
                        #Configuracion personalizada
                        #En teoría, sea el caso que aparecieron mas rostros en la foto.. se escogerá el primero en orden    
                        idUserDetected.append(idUserMatch.index(max(idUserMatch)))
                        #print(f"Usuario a mostrar: User{self.parent().IdUserToShow+1}")                    
                # Si no hay rostro, en las N verificaciones, consideramos que no habia nadie en frente y salimos del while
                else:
                    #print("No hay rostro detectado por la camara")
                    exitSleepMode=False
                    break
            #vs.stop()
            cam.release()
            if exitSleepMode:
                #De los usuarios detectados, nos quedamos con la moda
                #print("Usuarios detectados:",idUserDetected)
                from statistics import mode 
                self.parent().IdUserToShow=int(mode(idUserDetected))
                #Segun el usuario detectado, configuramos los GPIO
                self.parent().configureGPIOMirrol()
                #Detenemos este timer y habilitamos otro que actualizara Fecha, hora, botón, BT, entre otros
                self.timer_sondeaPresencia.stop()
                #Salimos del sleep mode y personalizamos!
                self.close()
                self.parent().timer_display.start(500)
                self.parent().timer_display_temp.start(20000)
                self.parent().timer_activeUser.start(10)
        # No hay persona ne frente
        else:
            self.parent().setColorLeds("noColor")
    
    def closeEvent(self, event):
        event.accept()

class BT_DialogBox (QtWidgets.QDialog):
    def __init__(self,parent=None):
        #print("entramos init BT dialog")
        super(BT_DialogBox,self).__init__(parent)
        #Desaparecemos el titleBar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        #Establecemos el tamaño de la pantalla
        self.setGeometry(0,0, WIDTH_SCREEN, HEIGHT_SCREEN)
        #Establecemos el fondo de color negro
        self.setStyleSheet("background:black")
        #creo el layout de nuestra ventana (vertical)
        self.layout=QtWidgets.QVBoxLayout()
        #Creo el texto a mostrar
        message = QtWidgets.QLabel("Se ha presionado el botón. Recibiendo información Bluetooth")
        message.setStyleSheet("font: 34pt \"Arial Rounded MT Bold\";color:white")
        message.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(message)
        #Creo la imagen
        image = QImage('resources/Bt.png')
        image=image.scaled(int(WIDTH_SCREEN/1.5), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)
        #Configuramos/actualizamos el layout
        self.setLayout(self.layout)
        #Abrir puerto
        self.ser = serial.Serial ("/dev/ttyS0", 9600,timeout=0.3)#timeout de 300ms
        #Flag
        self.ConfigRostro=False
        self.CloseWindow=False
        #Creamos timer para sondear datos
        self.timer_Datos=QTimer()
        self.timer_Datos.timeout.connect(self.sondeaDatos)
        self.timer_Datos.start(1)

    def sondeaDatos(self):
        if self.ConfigRostro:
            return
        #recibir data:   [funcion,idUser,color,BINtomacorrientes,altura]
        received_data = self.ser.read()              #read serial port
        # time.sleep(0.03)
        # data_left = self.ser.inWaiting()             #check for remaining byte
        # received_data += self.ser.read(data_left)
        if len(received_data)!=0:
            #Desactivamos sondeo, porque hemos recibido información. Lo activamos nuevamente al final
            #Esto lo hacemos para asegurar los tiempos entre timeouts
            self.timer_Datos.stop()
            #Decodificamos data
            #print("received data: ",received_data)
            received_data=eval(received_data.decode())
            #Con el primer elemento podemos revisar que función aplicamos
            if received_data[0]==0:
                """Trama de configurar rostro"""
                #print("Al usuario: ",received_data[1],"Le modificaremos su rostro")
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
                #print("El usuario: ",idUser,"tiene color: ", color)
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
                if altura>MAXIMA_ALTURA_ESPEJO:
                    altura=MAXIMA_ALTURA_ESPEJO
                #print("El usuario: ",idUser,"tiene color: ", color,"se activan:",BINtomacorrientes,"y altura:",altura)
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
                """VOLVEMOS A HACER UN PULL"""
                #Hacemos un pull en caso se actualizó el encodings.pickle desde una maquina externa
                from git import Repo
                repo = Repo(PATH_REPO)
                origin = repo.remote(name='origin')
                origin.pull()
                #Salimos del modo BtConnected
                self.close()
            else:
                print("función no creada")
            #Activamos sondeo, que habiamos desactivado al inicio
            if not(self.CloseWindow):
                self.timer_Datos.start()
        if gpio.input(self.parent().BUTTONpin)==False:
            #Button pressed. Verificamos si si pasan 3 segundos paara salir de este modo
            t=time.time()
            while gpio.input(self.parent().BUTTONpin)==False:
                time.sleep(0.2)
                if time.time()-t>3:
                    break
            t=time.time()-t
            if t>3:
                #Salimos del modo BtConnected
                #Guardamos los nuevos perfiles en un csv
                file=open("userConfig.csv","w")
                writer=csv.writer(file)
                parent=self.parent()
                perfiles=parent.perfiles
                for row in perfiles[0:-1]:
                    writer.writerow(row)
                file.close()
                """VOLVEMOS A HACER UN PULL"""
                #Hacemos un pull en caso se actualizó el encodings.pickle desde una maquina externa
                from git import Repo
                repo = Repo(PATH_REPO)
                origin = repo.remote(name='origin')
                origin.pull()
                #Salimos del modo BtConnected
                self.close()
                self.timer_Datos.stop()

            
    #Esta función por si sola nos permite aceptar el evento de cierre (not modified)
    def closeEvent(self, event):
        parent=self.parent()
        #activamos nuevamente el sondeo
        parent.timer_display.start(500)
        self.parent().timer_display_temp.start(20000)
        parent.timer_activeUser.start(10)
        self.CloseWindow=True
        #print("Salimos del BT mode")
        event.accept()

class configureUser_DialogBox (QtWidgets.QDialog):
    def __init__(self,parent=None,child=None,idUser=0):
        super(configureUser_DialogBox,self).__init__(parent)
        self.child=child
        #añadimos flag
        parent.AddingNewUser=True
        #Desaparecemos el titleBar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        #Establecemos el tamaño de la pantalla
        self.setGeometry(0,0, WIDTH_SCREEN, HEIGHT_SCREEN)
        #Establecemos el fondo de color negro
        self.setStyleSheet("background:black")
        #Colocamos una imagen de BT
        self.setWindowIcon(QtGui.QIcon('resources/RFLogo.png'))
        #Establecemos el tamaño
        self.resize(WIDTH_SCREEN, HEIGHT_SCREEN)
        #creo el layout de nuestra ventana (vertical)
        self.layout=QtWidgets.QVBoxLayout()
        #Creo el texto a mostrar
        self.message = QtWidgets.QLabel("Acérquese a la cámara")
        self.message.setStyleSheet("font: 34pt \"Arial Rounded MT Bold\";color:white")
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.message)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout)
        #seteando variables
        self.idUser=idUser
        parent.IdUserToShow=idUser
        self.frames=[]
        self.countPics=0
        self.picTaken=False
        self.ponerNuevaPose=True
        self.maxNumbersPics=20
        #Creamos unos widgets
        self.imageLabel = QtWidgets.QLabel()
        self.sencondLine = QtWidgets.QLabel("Coloque su rostro como muestra la imagen")   
        self.sencondLine.setStyleSheet("font: 42pt \"Arial Rounded MT Bold\";color:white")
        self.sencondLine.setAlignment(QtCore.Qt.AlignCenter)
        #Configuramos los timers
        self.timer_zero=QTimer()
        self.timer_zero.timeout.connect(self.initMirrolUp)
        self.timer_zero.start(800)
        self.timer_one=QTimer()
        self.timer_one.timeout.connect(self.takePicsNewUser)
        self.timer_two=QTimer()
        self.timer_two.timeout.connect(self.processPicsNewUser)
        #print("Salimos del init FR")
        
    def initMirrolUp(self):
        #detenemos el timer
        self.timer_zero.stop()
        self.parent().setColorLeds("blanco")
        self.parent().SubirEspejo()
        #print("Limit activado!")
        self.parent().actualAltura=MAXIMA_ALTURA_ESPEJO
        #Iniciamos los timer
        self.timer_one.start(800)        

    def takePicsNewUser(self):
        #print("Tomamos foto")
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
                    image=image.scaled(int(WIDTH_SCREEN/3), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
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
                    image=image.scaled(int(WIDTH_SCREEN/3), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
                    self.imageLabel.setPixmap(QPixmap.fromImage(image))
                    self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
                    self.setLayout(self.layout)#añadimos la imagen
                    self.ponerNuevaPose=False
            else:
                #Esta es la primera vez
                image=QImage('resources/'+imagenesFaceRecognition[self.countPics%6]+'.png')
                image=image.scaled(int(WIDTH_SCREEN/3), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
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
            #print("foto: ",self.countPics)
            #Guardamos la foto para hacer procesamiento
            self.frames.append(frame)
        
    def processPicsNewUser(self):
        #print("procesamos foto")
        if self.countPics==self.maxNumbersPics:
            #desahibiltamos el timer
            self.timer_two.stop()
            #Guardamos el nuevo pickle
            f = open("encodings.pickle", "wb")
            f.write(pickle.dumps(self.parent().knownEncodings))
            f.close()
            #Cerramos la ventana
            self.close()
            #Segun el usuario detectado, configuramos los GPIO
            self.parent().configureGPIOMirrol()
        """Realizamos el procesamiento"""
        frame=self.frames[self.countPics]
        # Lo pasamos a rgb
        rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Guardamos la imagen
        cv2.imwrite("dataset/user"+str(self.idUser)+"/image"+str(self.countPics)+".png",frame)
        
        # Actualizamos git haciendo un PUSH, para poder hacer procesamiento en maquina externa
        from git import Repo
        repo = Repo(PATH_REPO)
        #añadimos todos los archivos modificados
        repo.git.add('--all')
        #Añadimos comentario
        repo.git.commit('-m', f'usuario {self.idUser} foto N.{self.countPics}')
        origin = repo.remote(name='origin')
        origin.push() 
        
        #detectamos los rostros boxes
        boxes = FR_face_locations(rgb,model="hog") #Se escoge el modelo hog
        #obtenemos los encodings
        encodings = FR_face_encodings(rgb, boxes)
        # loop over the encodings
        tempEncodings=[]
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            tempEncodings.append(encoding)
        #Reemplazamos por los datos que ya teníamos
        self.parent().knownEncodings[self.idUser]=tempEncodings
        #Añadimos ventana de processing
        image=QImage('resources/'+imagenesProcessing[self.countPics%6])
        image=image.scaled(int(WIDTH_SCREEN/3), int(HEIGHT_SCREEN-40), QtCore.Qt.KeepAspectRatio)
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
        #Establecemos info por defecto
        # self.fecha_actual="viernes, 10 de junio del 2022"
        # self.hora_actual="18:00 pm"
        #self.temperatura_actual="00"
        #self.ui.temperatura.setText(self.temperatura_actual)   
        #Creamos unas variables flags
        self.initialization=True
        #Definimos unas variables
        self.maxDistance= 110#maxima distancia en cm del sensor
        self.maxTimeEcho= self.maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO en us
        self.minDistance= 30#minima distancia en cm del sensor
        self.minTimeEcho= self.minDistance*2/0.034 #en usec
        self.actualAltura=MAXIMA_ALTURA_ESPEJO
        self.countTimesSondeoBoton=0
        """Creamos distintos timer que realizarán un sondeo (Poll), actualizarán datos, checar{a el sleep entre otros"""
        # Timer para inicio de Mirroll
        self.timer_initMirroll= QTimer(self)
        self.timer_initMirroll.timeout.connect(self.initMirror)
        self.timer_initMirroll.start(10)
        # Creamos el timer cuando se tiene un usuario activo
        self.timer_activeUser=QTimer(self)
        self.timer_activeUser.timeout.connect(self.activeUser)
        # Timer que actualiza los display de la GUI cuando se tiene al usuario activo
        self.timer_display=QTimer(self)
        self.timer_display_temp=QTimer(self)
        self.timer_display.timeout.connect(self.displayFechayHora)
        self.timer_display_temp.timeout.connect(self.displayTemperatura) 
        
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
        self.CH2pin=11    
        self.CH3pin=9
        #Configuramos como salidas
        gpio.setup(self.CH1pin,gpio.OUT)
        gpio.setup(self.CH2pin,gpio.OUT)
        gpio.setup(self.CH3pin,gpio.OUT)
        #Configuramos todo en 
        gpio.output(self.CH1pin,gpio.HIGH)
        gpio.output(self.CH2pin,gpio.HIGH)
        gpio.output(self.CH3pin,gpio.HIGH)
        
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
        self.timer_initMirroll.stop()
        #Abrimos la ventana de modo Sleep
        dlg = sleepModeDialog(self)
        dlg.show()
        #Actualizamos la temperatura
        self.displayTemperatura()
        self.displayFechayHora()

    def activeUser(self):
        #Verificamos el boton y la presencia de usuario
        self.countTimesSondeoBoton+=1
        #print("count sondeo",self.countTimesSondeoBoton)
        if gpio.input(self.BUTTONpin)==False:
            #Detenemos el sondeo
            #print("Button pressed")
            self.timer_activeUser.stop()
            self.timer_display.stop()
            self.timer_display_temp.stop()
            #ponemos un popup de BT activado
            dlg = BT_DialogBox(self)
            dlg.show()
        if self.countTimesSondeoBoton==80:
            #print("sondeamos presencia")
            self.countTimesSondeoBoton=0
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
            #print("distancia: ",runnningTime*0.034/2)
            if runnningTime>self.maxTimeEcho:
                #print("Sensor, no detecta. Verificamos nuevamente y con camara")
                #Ya no hay persona al frente. Pero verificamos nuevamente
                """Calculamos nuevamente con el sensor y verificamos botón"""
                #Haacemos una espera de 1 segundo
                temp_t=time.time()+1
                #Mientras, verificamos si se presiona el boton
                while time.time()<temp_t:
                    if gpio.input(self.BUTTONpin)==False:
                        #Detenemos el sondeo
                        #print("Button pressed")
                        self.timer_display.stop()
                        self.timer_display_temp.stop()
                        self.timer_activeUser.stop()
                        #ponemos un popup de BT activado
                        dlg = BT_DialogBox(self)
                        dlg.show()
                        return
                #Activamos el sensor de ultrasonido                
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
                #print("distancia: ",runnningTime*0.034/2)
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
                    #Se ha ido la persona, apagamos los timers y nos vamos al modo sleep
                    #print("No hay nadie")
                    self.timer_activeUser.stop()
                    self.timer_display.stop()
                    self.timer_display_temp.stop()
                    #Abrimos el dialogo de modo sleep
                    dlg = sleepModeDialog(self)
                    dlg.show()
    
    def displayFechayHora(self):
        """Fecha"""
        currentFecha = QDate.currentDate()
        dia = currentFecha.toString('dddd')
        numero_dia = currentFecha.toString('dd')
        mes = currentFecha.toString('MMMM')
        anho = currentFecha.toString('yyyy')
        displayFecha = (dia + ', ' + numero_dia + ' de ' + mes + ' del ' + anho)
        self.ui.fecha.setText(displayFecha)
        """Hora"""
        currentHora = QTime.currentTime()
        displayHora = currentHora.toString('hh:mm')
        self.ui.hora.setText(displayHora)
    
    def displayTemperatura(self):
        response = requests.get(URL)
        # checking the status code of the request
        if response.status_code == 200:
            # getting data in the json format
            data = response.json()
            # getting the main dict block
            main = data['main']
            # getting temperature in string type
            temperature = str(int(main['temp']-273))
            # set value of temperature of Lima 
            self.ui.temperatura.setText(temperature)

    def configureGPIOMirrol(self):
        """Relés"""
        self.estadoS1= "1"==self.perfiles[self.IdUserToShow][2][0]
        self.estadoS2= "1"==self.perfiles[self.IdUserToShow][2][1]
        self.estadoS3= "1"==self.perfiles[self.IdUserToShow][2][2]
        #Chequeamos el estado
        if self.estadoS1 == False:
            #Hacemos la impresion que se tiene ha soltado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            gpio.output(self.CH1pin,gpio.HIGH)        
        else:
            #Hacemos la impresion que se tiene presionado el botón
            self.ui.botonS1.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            gpio.output(self.CH1pin,gpio.LOW)
        if self.estadoS2 == False:
            gpio.output(self.CH2pin,gpio.HIGH)
            self.ui.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
        else:
            gpio.output(self.CH2pin,gpio.LOW)
            self.ui.botonS2.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
            
        if self.estadoS3 == False:
            self.ui.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color: rgb(204, 204, 204)")
            gpio.output(self.CH3pin,gpio.HIGH)
        else:
            gpio.output(self.CH3pin,gpio.LOW)
            self.ui.botonS3.setStyleSheet("border-radius: 9px;\nbackground-color:rgb(216, 248, 232)")
        """Color"""
        idColor=self.perfiles[self.IdUserToShow][1]
        gpio.output(self.LREDpin,coloresGPIO[idColor][0])
        gpio.output(self.LGREENpin,coloresGPIO[idColor][1])
        gpio.output(self.LBLUEpin,coloresGPIO[idColor][2])
        """Altura motor"""
        diffAltura=self.perfiles[self.IdUserToShow][0]-self.actualAltura
        self.actualAltura=self.perfiles[self.IdUserToShow][0]
        if diffAltura<0:
            #Bajamos motor
            #print("bajamos motor")
            diffAltura=abs(diffAltura)
            self.BajarEspejo(diffAltura)
        elif diffAltura>0:
            #Subimos motor
            #print("subimos motor")
            self.SubirEspejo(diffAltura)
        #else:
            #mantenemos la altura
            #print("Dejamos la altura",self.actualAltura)

    def setColorLeds(self,color):
        #actualizamos el color
        idColor=colores.index(color)
        #Definimos los canales
        gpio.output(self.LREDpin,coloresGPIO[idColor][0])
        gpio.output(self.LGREENpin,coloresGPIO[idColor][1])
        gpio.output(self.LBLUEpin,coloresGPIO[idColor][2])
       
    def BajarEspejo(self,distancia=-1): 
        #Habilitamos el driver del motor
        gpio.output(self.ENApin,gpio.LOW)
        #Definimos la dirección
        gpio.output(self.DIRpin,gpio.LOW)
        #Primero iniciamos con un step time para una velocidad a la mitad de la de bajada
        initSteptime=STEPTIME*2 #En este caso será de de 1cm/seg la velocidad de subida
        #Luego de cierto tiempo aumentamos la velocidad a 2cm/seg
        timeSlowStep=2#en segundos
        initPulsesInSlow=(timeSlowStep*1000000000)/(initSteptime*2)#Para el caso de 1seg tenemos un total de 4000 pulsos
        tempSteptime=initSteptime
        adderStepTime=(STEPTIME-initSteptime)/initPulsesInSlow
        if distancia==-1:
            #Bajamos el espejo hasta sentir el limit switch
            while gpio.input(self.LSDOWNpin)==0:
                if tempSteptime<=STEPTIME:
                    tempSteptime=STEPTIME
                else:
                    tempSteptime+=adderStepTime
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass

                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
            self.actualAltura=MINIMA_ALTURA_ESPEJO
        else:
            #Bajamos una cierta altura o hasta sentir el Limit switch
            for i in range(int(distancia*PULSES_PER_DIST)):
                if tempSteptime<=STEPTIME:
                    tempSteptime=STEPTIME
                else:
                    tempSteptime+=adderStepTime
                
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
                
                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
                #Verificamos limit SW
                if gpio.input(self.LSDOWNpin)!=0:
                    self.actualAltura=MINIMA_ALTURA_ESPEJO
                    break
        gpio.output(self.ENApin,gpio.HIGH)
    
    def SubirEspejo(self,distancia=-1): 
        #Habilitamos el driver del motor
        gpio.output(self.ENApin,gpio.LOW)
        #Definimos la dirección
        gpio.output(self.DIRpin,gpio.HIGH)
        #Primero iniciamos con un step time para una velocidad a la mitad de la de bajada
        initSteptime=STEPTIME*2 #En este caso será de de 1cm/seg la velocidad de subida
        #Luego de cierto tiempo aumentamos la velocidad a 2cm/seg
        timeSlowStep=2#en segundos
        initPulsesInSlow=(timeSlowStep*1000000000)/(initSteptime*2)#Para el caso de 1seg tenemos un total de 4000 pulsos
        tempSteptime=initSteptime
        adderStepTime=(STEPTIME-initSteptime)/initPulsesInSlow
        if distancia==-1:
            #Subimos el espejo hasta sentir el limit switch
            while gpio.input(self.LSUPpin)==0:#notar que se detiene en flanco de subida!
                if tempSteptime<=STEPTIME:
                    tempSteptime=STEPTIME
                else:
                    tempSteptime+=adderStepTime
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
            self.actualAltura=MAXIMA_ALTURA_ESPEJO
        else:
            #Subimos el espejo una cierta altura o hasta sentir el limit switch
            for i in range(int(distancia*PULSES_PER_DIST)):
                if tempSteptime<=STEPTIME:
                    tempSteptime=STEPTIME
                else:
                    tempSteptime+=adderStepTime
                
                #Ponemos en HIGH
                gpio.output(self.PULpin,gpio.HIGH)        
                #Esperamos en HIGH
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
                
                #Ponemos en LOW
                gpio.output(self.PULpin,gpio.LOW)        
                #Esperamos en LOW
                initTime=time.time_ns()
                while time.time_ns()-initTime<tempSteptime:
                    pass
                #Verificamos limit SW
                if gpio.input(self.LSUPpin)!=0:
                    self.actualAltura=MAXIMA_ALTURA_ESPEJO
                    break
        #Deshabilitamos el driver del motor
        gpio.output(self.ENApin,gpio.HIGH)

""" //////////////////////////////////////////
    //                Main                  //
    //////////////////////////////////////////
""" 
stylesheet="""
    QMainWindow{
        background:black
    }
"""
def setUpMirrollGUI():
    import sys
    #Creamos la app
    app = QtWidgets.QApplication(sys.argv)  
    #Colocamos background
    app.setStyleSheet(stylesheet)
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