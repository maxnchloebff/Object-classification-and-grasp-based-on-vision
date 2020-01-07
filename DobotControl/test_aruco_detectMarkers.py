import numpy as np
import cv2
import cv2.aruco as aruco

img = cv2.imread('build/singlemarkersoriginal.png')
cv2.namedWindow("Image")
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

# lists of ids and the corners belonging to each id
corners, ids, projectedImgPoints = aruco.detectMarkers(gray_img, aruco_dict, parameters=parameters)

color_image = aruco.drawDetectedMarkers(img, projectedImgPoints)

cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
