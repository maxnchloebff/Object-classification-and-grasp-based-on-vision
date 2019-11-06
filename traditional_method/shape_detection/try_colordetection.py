from traditional_method.shape_detection.pyimagesearch.ImageType import Image
import cv2
import numpy as np
import imutils
low_blue = (100,90,90)
hight_blue = (140,255,255)

image_name = 'adjoin.png'
im_orig = cv2.imread(image_name)
im_hsv = cv2.cvtColor(im_orig,code=cv2.COLOR_BGR2HSV)
hsv_channels = cv2.split(im_hsv)
cv2.equalizeHist(hsv_channels[2],hsv_channels[2])
im_hsv = cv2.merge(hsv_channels)
im_hsv_thre = cv2.inRange(im_hsv,low_blue,hight_blue)
# 去除噪点 开操作
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
im_hsv = cv2.morphologyEx(im_hsv_thre,cv2.MORPH_OPEN,kernel)
# 闭操作（连通区域）
im_hsv = cv2.morphologyEx(im_hsv_thre,cv2.MORPH_CLOSE,kernel)
cnts = cv2.findContours(im_hsv, cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
for cnt in cnts:
    m = cv2.moments(cnt)
    cx = int((m["m10"] / m["m00"]) )
    cy = int((m["m01"] / m["m00"]) )
    peri = cv2.arcLength(cnt, True)
    # approx is the collection of corner points
    approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
    #  convert the corner points into the list format
    corner_points = [[point[0][0], point[0][1]] for point in approx]
# im_bgr = cv2.cvtColor(im_hsv_thre,code=cv2.COLOR_HSV2BGR_FULL)

cv2.imshow(' ',im_hsv)
cv2.imshow('original',im_orig)
cv2.waitKey(0)