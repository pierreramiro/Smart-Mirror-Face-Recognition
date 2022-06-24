from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Librería para el control del Raspberry
import RPi.GPIO as gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

#libreria para el face recog
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

#LOAD ENCODINGS DATA
encodingsP = "encodings.pickle"
data = pickle.loads(open(encodingsP, "rb").read())

######## CONTROL SENSOR #######
ECHOpin=12
TRIGpin=16
#Configuramos como entrada
gpio.setup(ECHOpin,gpio.IN,pull_up_down=gpio.PUD_DOWN)
#Configuramos como salida
gpio.setup(TRIGpin,gpio.OUT)
gpio.output(TRIGpin,gpio.LOW)
maxDistance= 100#maxima distancia en cm
maxTimeEcho= maxDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO
minDistance= 60#maxima distancia en cm
minTimeEcho= minDistance*2/0.034  #Calculamos el tiempo máximo aceptado por el ECHO

import time


def takePic(fileName):
    cam=cv2.VideoCapture(0)
    ret,frame=cam.read()
    cv2.imwrite(fileName,frame)
    cam.release()

def sondeaSensor():
    #medimos la distancia del sensor ultrasonido
    #tiempo de muestreo
    gpio.output(TRIGpin,gpio.HIGH)
    t1=time.time()
    #esperamos a cumplir los 10usec
    while time.time()<t1+0.000015: #nosotros esperamos hasta 15us
        pass
    gpio.output(TRIGpin,gpio.LOW)
    #Esperamos el echo en HIGH
    while not(gpio.input(ECHOpin)):
        pass
    t1=time.time()
    #Esperamos el echo en flanco de bajada
    while gpio.input(ECHOpin):
        pass
    runnningTime=(time.time()-t1)*1000000
    if runnningTime<maxTimeEcho and runnningTime>minTimeEcho: 
        #Tenemos una persona en frente!
        print("Persona a distancia:",runnningTime*0.034/2)
        
        """Procedemos a realizar el face recognition"""
        cam=cv2.VideoCapture(0)
        ret,frame=cam.read()
        cam.release()
        frame = imutils.resize(frame, width=500)
        # Detect the face boxes
        boxes = face_recognition.face_locations(frame)
        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(frame, boxes)

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],encoding)
            name = "Deconocido" #if face is not recognized, then print Unknown
            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (NOTE: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

                print("Hola",name,"!")
                # #If someone in your dataset is identified, print their name on the screen
                # if currentname != name:
                #     currentname = name
                #     print(currentname)
            

if __name__ == "__main__":
    while True:
        time.sleep(0.5)
        sondeaSensor()