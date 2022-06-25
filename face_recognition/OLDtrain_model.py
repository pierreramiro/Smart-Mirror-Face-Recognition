#! /usr/bin/python

# import the necessary packages
from imutils import paths
import face_recognition
#import argparse
import pickle
import cv2
import os

# our images are located in the dataset folder
print("[INFO] start processing faces...")
imagePaths = list(paths.list_images("dataset"))

# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
	# Print how the training is going
	print("[INFO] processing image {}/{}".format(i + 1,len(imagePaths))) #we process all images of all persons
	# extract the person name from the image path
	name = imagePath.split(os.path.sep)[-2] 

	# load the input image and convert it from RGB (OpenCV ordering) to dlib ordering (RGB)
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Esto es importante, para poder entrenar a la red

	# detect the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
	boxes = face_recognition.face_locations(rgb,model="hog") #Se escoge el modelo hog

	# compute the facial embedding for the face
	encodings = face_recognition.face_encodings(rgb, boxes)

	# loop over the encodings
	for encoding in encodings:
		# add each encoding + name to our set of known names and
		# encodings
		knownEncodings.append(encoding)
		knownNames.append(name)

# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open("OLDencodings.pickle", "wb")
f.write(pickle.dumps(data))
f.close()
