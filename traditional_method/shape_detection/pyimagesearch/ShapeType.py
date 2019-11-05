import numpy as np
import math


def get_calibration(shape_name, orientation='clockwise'):
    """
    ！！！！！！
    任何正多边形都没有标准型，但是必须满足首个vector的角度为0，且顺时针转动，
    或者首个向量的角度为180，逆时针转动
    ！！！！！！
    三角形的标准：第一条向量为最长向量，且角度为0，顺时针转动，或者角度为180，逆时针转动
    四边形的标准：
        长方形：长边为第一条向量，且角度为0，顺时针转动，或者角度为180，逆时针转动
        菱形：第一个向量角度为0，顺时针转动，内角为锐角，或者180，逆时针转动，内较为钝角
        平行四边形：第一条向量为长边，角度为0，顺时针转动，或者180，逆时针转动
        梯形：第一条边为长底，角度为0度，顺时针转动，或者角度为180，逆时针转动。
    五边形暂时都处理为正五边形
    圆不存在旋转角度
    :param shape_name: shape‘s name
    :param orientation: clockwise or counterclockwise
    :return: the order of the length
    """
    if shape_name == 'triangle':
        if orientation == 'clockwise':
            length_order = [2, 1, 0]
        else:
            length_order = [2, 0, 1]
        return length_order

    if shape_name == 'rectangle'  or shape_name == 'parallelogram':
        if orientation == 'clockwise':
            length_order = [1, 0]
        else:
            length_order = [0, 1, 2]
class Shape:

    def __init__(self, corner_points):
        self.shape_name = None
        self.num_points = len(corner_points)
        self.corner_points = np.array(corner_points)
        self.mass_point = self.corner_points.mean(axis=0)
        self.central_corner_points = self.corner_points - np.tile(self.mass_point, (self.num_points, 1))

        self.vectors = self.central_corner_points - np.insert(
            self.central_corner_points[:-1, :], 0, self.central_corner_points[-1, :], axis=0)
        # calculate the cross product then if > 0 it's clockwise,
        # if else then counterclockwise.(Since the coordinate in opencv is different)
        self.orientation = 'clockwise' if np.cross(self.vectors[0], self.vectors[1]) > 0 else 'counter_clockwise'
        # calculate the line angles
        self.lines_angles = []
        for vector in self.vectors:
            angle = int(math.atan2(vector[1], vector[0])*180/math.pi)
            self.lines_angles.append(angle)
        self.lines_angles = np.asanyarray(self.lines_angles)
        self.intersection_angles = (np.insert(self.lines_angles[:-1], 0, self.lines_angles[-1]) - self.lines_angles) % 360
        self.lengths = np.linalg.norm(self.vectors, axis=1)


    def determine_shape(self):

        if self.num_points == 3:
            self.shape_name = "triangle"

        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif self.num_points == 4:

            judgement_rectangle = self.intersection_angles.std() / self.intersection_angles.mean() < 0.1
            if judgement_rectangle:
                judgement_square = self.lengths.std() / self.lengths.mean() < 0.1
                if judgement_square:
                    self.shape_name = 'square'
                else:
                    self.shape_name = 'rectangle'
            else:
                if abs(abs(self.lines_angles[0] - self.lines_angles[2]) - 180) < 5 and abs(
                        abs(self.lines_angles[1] - self.lines_angles[3]) - 180) < 5:
                    judgement_diamond = self.lengths.std() / self.lengths.mean() < 0.1
                    if judgement_diamond:
                        self.shape_name = 'diamond'
                    else:
                        self.shape_name = 'parallelogram'
                elif abs(abs(self.lines_angles[0] - self.lines_angles[2]) - 180) < 5 or abs(
                        abs(self.lines_angles[1] - self.lines_angles[3]) - 180) < 5:
                    self.shape_name = 'ladder'

        # if the shape is a pentagon, it will have 5 vertices
        elif self.num_points == 5:
            self.shape_name = "pentagon"

        # otherwise, we assume the shape is a circle
        else:
            self.shape_name = "circle"

        return self.shape_name

    def determine_rotation(self):
        length_order = get_calibration(self.shape_name,self.orientation)
        self.lengths.sort()
