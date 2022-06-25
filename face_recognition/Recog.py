import time
import cv2
from imutils.video import VideoStream

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

def takePicAndDetect_vs():
    vs = VideoStream(src=0,framerate=10).start()
    frame=vs.read()
    cv2.imwrite("1.jpg",frame)
    vs.stop()
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
    takePicAndDetect_vs()