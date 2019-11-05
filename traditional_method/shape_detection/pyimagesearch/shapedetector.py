# import the necessary packages
import cv2
import math
import operator
import numpy as np
from traditional_method.shape_detection.pyimagesearch.ShapeType import Shape
import imutils


class Image:

    def __init__(self,debug):
        self.debug = debug
        self.original_image = None
        self.after_thresh = None
        self.Shapes = []

    def read_image(self,image):
        """
        read an image from source
        :param image: the original image source
        :return: the image after threshhold operation
        """
        self.original_image = cv2.imread(image)
        self.resized = imutils.resize(self.original_image, width=300)
        self.ratio = self.original_image.shape[0] / float(self.resized.shape[0])
        # convert the resized image to grayscale, blur it slightly,
        # and threshold it
        gray = cv2.cvtColor(self.resized, cv2.COLOR_BGR2GRAY)
        if self.debug is True:
            cv2.imshow('after_gray', gray)
            cv2.waitKey(0)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        if self.debug is True:
            cv2.imshow('after_blurred', blurred)
            cv2.waitKey(0)
        if image == 'shapes_and_colors.png':
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        else:
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)[1]

        if self.debug is True:
            cv2.imshow('after_thresh', self.after_thresh)
            cv2.waitKey(0)
        return self.after_thresh

    def reset(self):
        self.original_image = None
        self.after_thresh = None
        self.Shapes = []

    def detect_shapes(self):
        cnts = cv2.findContours(self.after_thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)
        if self.debug == True:
            cv2.drawContours(self.resized, cnts, -1, (255, 0, 0), thickness=8)
            cv2.imshow('draw_contour', self.resized)
            cv2.waitKey(0)
        for cnt in cnts:
            M = cv2.moments(cnt)
            cX = int((M["m10"] / M["m00"]) * self.ratio)
            cY = int((M["m01"] / M["m00"]) * self.ratio)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            corner_points = [[point[0][0], point[0][1]] for point in approx]
            curren_shape = Shape(corner_points)
            shape_nm = curren_shape.determin_shape()
            cnt = cnt.astype("float")
            cnt *= self.ratio
            cnt = cnt.astype("int")
            image_copy = self.original_image.copy()
            cv2.drawContours(image_copy, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(image_copy, shape_nm, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)

            # show the output image
            cv2.imshow("Image", image_copy)
            cv2.waitKey(0)

def cal_angle(v1, v2):
    angle1 = math.atan2(v1[1], v1[0])
    angle1 = int(angle1 * 180 / math.pi)
    angle2 = math.atan2(v2[1], v2[0])
    angle2 = int(angle2 * 180 / math.pi)
    if angle1 * angle2 >= 0:
        included_angle = abs(angle1 - angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    return included_angle


def get_calibration(shape_name, orientation='clockwise'):
    if shape_name == 'triangle':
        if orientation == 'clockwise':
            length_order = [0, 2, 1]
        else:
            length_order = [0, 1, 2]
        return length_order


if __name__ == '__main__':
    image = Image(debug=True)
    image.read_image('../ladder.png')
    image.detect_shapes()