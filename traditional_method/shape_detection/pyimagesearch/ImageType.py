# import the necessary packages
import cv2
import math
from traditional_method.shape_detection.pyimagesearch.ShapeType import Shape
import imutils
class ImageNotExistError(ValueError):

    def __init__(self,message='No existing image after threshold!!!!!'):
        super().__init__(message)
        self.message = message


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
        if image_name == 'shapes_and_colors.png':
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        else:
            self.after_thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)[1]

        if self.debug is True:
            cv2.imshow('after_thresh', self.after_thresh)
            cv2.waitKey(0)
        return self.after_thresh

    def reset(self):
        self.original_image = None
        self.resized = None
        self.ratio = None
        self.after_thresh = None
        self.Shapes = []

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
        cnts = cv2.findContours(self.after_thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)
        if self.debug is True:
            cv2.drawContours(self.resized, cnts, -1, (255, 0, 0), thickness=8)
            cv2.imshow('draw_contour', self.resized)
            cv2.waitKey(0)
        if len(cnts) == 0:
            self.reset()
            print('There is no contours in the current image. Try another image!!!!')
            return False
        for cnt in cnts:
            m = cv2.moments(cnt)
            cx = int((m["m10"] / m["m00"]) * self.ratio)
            cy = int((m["m01"] / m["m00"]) * self.ratio)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            corner_points = [[point[0][0], point[0][1]] for point in approx]
            current_shape = Shape(corner_points)
            # detect the shape
            shape_nm = current_shape.determine_shape()
            # detect rotation based on calibration
            current_shape.determine_rotation()
            self.Shapes.append(current_shape)
            cnt = cnt.astype("float")
            cnt *= self.ratio
            cnt = cnt.astype("int")
            image_copy = self.original_image.copy()
            cv2.drawContours(image_copy, [cnt], -1, (0, 255, 0), 2)
            cv2.putText(image_copy, shape_nm, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
            cv2.putText(image_copy, str(current_shape.angle_deviation), (cx, cy+20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)

            # show the output image
            cv2.imshow("Image", image_copy)
            cv2.waitKey(0)
        return True






if __name__ == '__main__':

    image = Image(debug=True)
    image.read_image('../ladder.png')
    image.detect_shapes()