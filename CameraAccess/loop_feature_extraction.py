import numpy as np
import cv2
from ctypes import *

# call API to query image
dll = cdll.LoadLibrary("JHCap2.dll")
# Camera parameter settings
dll.CameraInit(0)
dll.CameraSetResolution(0, 0, 0, 0)
dll.CameraSetContrast.argtypes = [c_int, c_double]
dll.CameraSetGain(0, 0, 0, 5)
dll.CameraSetContrast(0, 1)
dll.CameraSetExposure(0, 1265)
buflen = c_int()
width = c_int()
height = c_int()
dll.CameraGetImageSize(0, byref(width), byref(height))
dll.CameraGetImageBufferSize(0, byref(buflen), 0x4)
inbuf = create_string_buffer(buflen.value)

# cv2 settings
detector = cv2.ORB_create()
cv2.namedWindow("s")

while True:
	dll.CameraQueryImage(0, inbuf, byref(buflen), 0x104)
	arr = np.frombuffer(inbuf, np.uint8)
	img = np.reshape(arr, (height.value, width.value, 3))

	# Write your image processing here
	kp = detector.detect(img, None)
	kp = kp[:100]
	kp, des = detector.compute(img, kp)
	cv2.drawKeypoints(img, kp, img, (255, 0, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	img = cv2.resize(img, (640, 480))

	cv2.imshow("s", img)
	key = cv2.waitKey(33)  # change parameter according to frame rate, wait time = 1000/fps
	if (key & 0xff) == 27:  # press ESC on image window to terminate the loop
		break
cv2.destroyWindow("s")
