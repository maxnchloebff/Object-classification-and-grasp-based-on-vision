# import the necessary packages
import cv2
import math
from traditional_method.shape_detection.pyimagesearch.ShapeType import Shape
import imutils


class ImageNotExistError(ValueError):

    def __init__(self, message='No existing image after threshold!!!!!'):
        super().__init__(message)
        self.message = message


def draw_a_point(img, point: tuple, color: tuple, radius: int):
    cv2.circle(img, point, radius, color, thickness=-1)


class Image:
    """
    Image class should contends a list of Shape class
    First read an image to convert it into binary image,
    then detect the shape information from image after threshold
    """

    def __init__(self, debug):
        self.debug = debug
        self.original_image = None
        self.resized = None
        self.ratio = None
        self.after_thresh = None
        self.Shapes = []

    def only_read(self, image_name):
        self.original_image = cv2.imread(image_name)

    def read_image(self, image_name):
        """
        read an image from source
        :param image_name: the original image source
        :return: the image after threshold operation
        """
        self.original_image = cv2.imread(image_name)
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
        if image_name == 'ladder.png':
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)[1]
        else:
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

        if self.debug is True:
            cv2.imshow('after_thresh', self.after_thresh)
            cv2.waitKey(0)
        return self.after_thresh

    def detect_by_color(self, color, draw=False):

        if color == 'blue':
            low = (100, 90, 90)
            high = (140, 255, 255)
        elif color == 'red':
            low = (160, 90, 90)
            high = (179, 255, 255)
        elif color == 'green':
            low = (38, 90, 90)
            high = (75, 255, 255)
        else:
            print('no such color')
        im_hsv = cv2.cvtColor(self.original_image, code=cv2.COLOR_BGR2HSV)
        hsv_channels = cv2.split(im_hsv)
        cv2.equalizeHist(hsv_channels[2], hsv_channels[2])
        im_hsv = cv2.merge(hsv_channels)
        im_hsv_thre = cv2.inRange(im_hsv, low, high)
        # 去除噪点 开操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        im_hsv = cv2.morphologyEx(im_hsv_thre, cv2.MORPH_OPEN, kernel)
        # 闭操作（连通区域）
        im_hsv = cv2.morphologyEx(im_hsv, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(im_hsv, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) == 0:
            # self.reset()
            print('There is no contours in {}. Try another image!!!!'.format(color))
            return False
        for cnt in cnts:
            m = cv2.moments(cnt)
            cx = int((m["m10"] / m["m00"]))
            cy = int((m["m01"] / m["m00"]))
            peri = cv2.arcLength(cnt, True)
            # approx is the collection of corner points
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            #  convert the corner points into the list format
            corner_points = [[point[0][0], point[0][1]] for point in approx]
            current_shape, shape_nm, angle_deviation, orientation, catch_point = self.detect_from_corner_points(corner_points, color)
            if draw is True:
                image_copy = self.draw_cnt_with_name_and_rotation(cnt, shape_nm, cx, cy, angle_deviation, orientation, catch_point)
                # show the output image
                draw_a_point(image_copy, (int(current_shape.mass_point[0]), int(current_shape.mass_point[1])), color=(255, 0, 0), radius=4)
                cv2.imshow("Image", image_copy)
                cv2.waitKey(0)
        return True

    def reset(self):
        self.original_image = None
        self.resized = None
        self.ratio = None
        self.after_thresh = None
        self.Shapes = []

    def detect_from_corner_points(self, corner_points, color):
        current_shape = Shape(corner_points, color)
        # detect the shape shape_nm is string(name)
        shape_nm = current_shape.determine_shape()
        # detect rotation based on calibration
        angle_deviation, orientation = current_shape.determine_rotation()
        catch_point = current_shape.determine_catch_point()
        self.Shapes.append(current_shape)
        return current_shape, shape_nm, angle_deviation, orientation, catch_point

    def draw_cnt_with_name_and_rotation(self, cnt, shape_nm, cx, cy, angle_deviation, orientation, catch_point):
        cnt = cnt.astype("float")
        cnt = cnt.astype("int")
        image_copy = self.original_image.copy()
        cv2.drawContours(image_copy, [cnt], -1, (0, 255, 0), 2)
        cv2.putText(image_copy, shape_nm, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
        cv2.putText(image_copy, str(angle_deviation) + '  ' + str(orientation), (cx, cy + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
        if catch_point is not None:
            cv2.circle(img=image_copy, center=(int(catch_point[0]), int(catch_point[1])), radius=20, thickness=-1,
                       color=(255, 0, 255))
        return image_copy

    def detect_shapes(self):
        """
        detect the basic shapes in current image,then return the status,True for having shapes, False for having no shapes.
        If there is no contours in the image, then reset the Image class.
        :return: status(True or False)
        """
        # if there is no existing image in the Image class then raise an exception and exit
        if self.original_image is None:
            try:
                raise ImageNotExistError
            except ImageNotExistError as e:
                print(e.message)
                exit(1)
        # find the contours in the 'after thresh'
        cnts = cv2.findContours(self.after_thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)
        if self.debug is True:
            cv2.drawContours(self.resized, cnts, -1, (255, 0, 0), thickness=8)
            cv2.imshow('draw_contour', self.resized)
            cv2.waitKey(0)
        # if no existing contour then return False
        if len(cnts) == 0:
            self.reset()
            print('There is no contours in the current image. Try another image!!!!')
            return False
        # if exists then>>>>>
        for cnt in cnts:
            m = cv2.moments(cnt)
            cx = int((m["m10"] / m["m00"]) * self.ratio)
            cy = int((m["m01"] / m["m00"]) * self.ratio)
            peri = cv2.arcLength(cnt, True)
            # approx is the collection of corner points
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            #  convert the corner points into the list format
            corner_points = [[point[0][0], point[0][1]] for point in approx]
            # initialize thew shape class
            shape_nm, angle_deviation, orientation, catch_point = self.detect_from_corner_points(corner_points,
                                                                                                 color=None)
            self.draw_cnt_with_name_and_rotation(cnt, shape_nm, cx, cy, angle_deviation, orientation, catch_point)
        return True


if __name__ == '__main__':
    image = Image(debug=True)

    image.read_image('../shapes_and_colors.png')
    image.detect_shapes()
    image.reset()
