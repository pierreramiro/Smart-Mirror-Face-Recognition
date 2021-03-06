#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import numpy as np

#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "Desconocido"
#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar cascade for face detection (hog)
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
users=["user0","user1","user2","user3","user4","user5","user6","user7","user8","user9"]
# initialize the video stream and allow the camera sensor to warm up
# Set the src to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
vs = VideoStream(src=0,framerate=10).start()
cam=cv2.VideoCapture(0)
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream and resize it to 500px (to speedup processing)
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	# Detect the face boxes
	boxes = face_recognition.face_locations(frame)
	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(frame, boxes)
	names = []
	idUser=[0]*10
	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known encodings
		for id,dataEncs in enumerate(data):
			matches=face_recognition.compare_faces(dataEncs,encoding)
			#print(len(matches))
			idUser[id]+=matches.count(True) 
		
		name = "Deconocido" #if face is not recognized, then print Unknown
		name=users[idUser.index(max(idUser))]
		#If someone in your dataset is identified, print their name on the screen
		if currentname != name:
			currentname = name
			print(currentname)

		# update the list of names
		names.append(name)

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image - color is in BGR
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 225), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			.8, (0, 255, 255), 2)

	# display the image to our screen
	cv2.imshow("Facial Recognition is Running", frame)
	key = cv2.waitKey(1) & 0xFF

	# quit when 'q' key is pressed
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
