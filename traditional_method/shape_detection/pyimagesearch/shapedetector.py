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


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        info = []
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        corner_points = [[point[0][0], point[0][1]] for point in approx]
        mass_point = [0, 0]
        for point in corner_points:
            mass_point[0] += point[0]
            mass_point[1] += point[1]
        mass_point[0] /= len(corner_points)
        mass_point[1] /= len(corner_points)
        cenral_corner_points = [[point[0] - mass_point[0], point[1] - mass_point[1]] for point in corner_points]
        vectors = [[(corner_points[i][0] - corner_points[i - 1][0]), (corner_points[i][1] - corner_points[i - 1][1])]
                   for i in range(len(corner_points))]
        angles = []
        for i in range(len(vectors)):
            angles.append(int(math.atan2(vectors[i][1], vectors[i][0]) * 180 / math.pi))

        angles_between = []
        for i in range(len(vectors) - 1):
            angles_between.append(cal_angle(vectors[i], vectors[i + 1]))
        angles_between.append(cal_angle(vectors[-1], vectors[0]))
        # order the the corner points according to the length of each vector
        lengths = []
        for i in range(len(vectors)):
            lengths.append([pow(vectors[i][0], 2) + pow(vectors[i][1], 2), i])
        lengths.sort(key=lambda x: x[0])
        length_order = [pair[1] for pair in lengths]
        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
            cali_order = get_calibration(shape)
            first_cali_element = cali_order[0]
            first_actual_element = length_order[0]
            move = abs(first_actual_element - first_cali_element) % 3
            angle = math.atan2(vectors[move][1], vectors[move][0])
            angle = int(angle * 180 / math.pi)



        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio

            angles_between_array = np.abs(np.array(angles_between))
            judgement_rectangle = angles_between_array.std() / angles_between_array.mean() < 0.1
            if judgement_rectangle:
                lengths_array = np.array(lengths)
                judgement_square = lengths_array.std(axis=0)[0] / lengths_array.mean(axis=0)[0] < 0.1
                if judgement_square:
                    shape = 'square'
                else:
                    shape = 'rectangle'
            else:
                vectors_array = np.array(vectors)
                angles_array = np.array(angles)
                if abs(abs(angles_array[0] - angles_array[2]) - 180) < 5 and abs(
                        abs(angles_array[1] - angles_array[3]) - 180) < 5:
                    lengths_array = np.array(lengths)
                    judgement_diamond = lengths_array.std(axis=0)[0] / lengths_array.mean(axis=0)[0] < 0.1
                    if judgement_diamond:
                        shape = 'diamond'
                    else:
                        shape = 'parallelogram'
                elif abs(abs(angles_array[0] - angles_array[2]) - 180) < 5 or abs(
                        abs(angles_array[1] - angles_array[3]) - 180) < 5:
                    shape = 'ladder'

            if shape == 'square':
                absAngles = map(abs, angles)
                absAngles = list(absAngles)
                absAngles.sort(key=lambda x: min(180 - x, x))
                angle = angles[absAngles.index(min(absAngles))]
                if angle > 90:
                    angle = 180 - angle
            else:
                absAngles = map(abs, angles)
                absAngles = list(absAngles)
                absAngles.sort(key=lambda x: min(180 - x, x))
                angle = angles[absAngles.index(min(absAngles))]
                if angle > 90:
                    angle = 180 - angle

        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
            absAngles = map(abs, angles)
            absAngles = list(absAngles)
            absAngles.sort(key=lambda x: min(180 - x, x))
            angle = angles[absAngles.index(min(absAngles))]


        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
            angle = None

        # return the name of the shape
        return shape, approx, angle

if __name__ == '__main__':
    image = Image(debug=True)
    image.read_image('../ladder.png')
    image.detect_shapes()