# USAGE
# python detect_shapes.py --image shapes_and_colors.png

import argparse
import numpy as np

import cv2
import imutils
# import the necessary packages
from traditional_method.shape_detection.pyimagesearch.shapedetector import ShapeDetector

# construct the argument parse and parse the arguments

array_add = np.array([1,2,3,4])
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-d", "--debug", required=False, default=True,
	help="whether to set the debug mode(draw some pictures)")
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
image = cv2.imread(args["image"])
debug = args['debug']
resized = imutils.resize(image, width=300)
ratio = image.shape[0] / float(resized.shape[0])

# convert the resized image to grayscale, blur it slightly,
# and threshold it
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
if debug == True:
	cv2.imshow('after_thresh',gray)
	cv2.waitKey(0)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
if debug == True:
	cv2.imshow('after_thresh',blurred)
	cv2.waitKey(0)

thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
if debug == True:
	cv2.imshow('after_thresh',thresh)
	cv2.waitKey(0)

# find contours in the thresholded image and initialize the
# shape detector
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)

cnts = imutils.grab_contours(cnts)
if debug == True:
	cv2.drawContours(resized,cnts,-1,(255,0,0), thickness=8)
	cv2.imshow('draw_contour',resized)
	cv2.waitKey(0)
sd = ShapeDetector()

# loop over the contours
for c in cnts:
	# compute the center of the contour, then detect the name of the
	# shape using only the contour
	M = cv2.moments(c)
	cX = int((M["m10"] / M["m00"]) * ratio)
	cY = int((M["m01"] / M["m00"]) * ratio)
	shape,corner_points,angle = sd.detect(c)

	# multiply the contour (x, y)-coordinates by the resize ratio,
	# then draw the contours and the name of the shape on the image
	c = c.astype("float")
	c *= ratio
	c = c.astype("int")
	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	cv2.putText(image, shape+' '+str(angle)+'Degree', (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
		0.5, (255, 255, 255), 2)

	# show the output image
	cv2.imshow("Image", image)
	cv2.waitKey(0)