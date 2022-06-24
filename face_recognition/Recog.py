import sys
from tkinter import Button
from turtle import distance

from click import echo
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Librería para el control del Raspberry
import RPi.GPIO as gpio
gpio.setwarnings(False)

import time
import cv2
#Liberia para

def takePicAndDetect():
    cam=cv2.VideoCapture(0)
    ret,frame=cam.read()
    cv2.imwrite("1.jpg",frame)
    cam.release()
    face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray,1.1,4)
    if len(faces)==0:
        print("No cara")
    else:
        print("hay cara")


if __name__ == "__main__":
    # print(type(cv2.imread("1.jpg")))
    # cam=cv2.VideoCapture(0)
    # ret,frame=cam.read()
    # cv2.imwrite("1.jpg",frame)
    # cam.release()
    # print(type(frame))
    takePicAndDetect()