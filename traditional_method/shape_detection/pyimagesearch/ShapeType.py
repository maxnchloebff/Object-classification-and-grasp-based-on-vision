import numpy as np
import math

class NotAShape(Exception):

    def __init__(self,message='Corner_Points list only contains less than 2 points!!!!'):
        super().__init__(message)
        self.message = message


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
    每一个标准型的最小边的边长是1！！！！！！！
    所以要将每一个图型乘以相应倍数才可！！！！！！！！
    :param shape_name: shape‘s name
    :param orientation: clockwise or counterclockwise
    :return: the order of the length
    """
    catch_point = None
    if shape_name == 'triangle':
        if orientation == 'clockwise':
            length_order = [2, 1, 0]
        else:
            length_order = [2, 0, 1]
    if shape_name == 'equilateral triangle':
        catch_point = np.array([0.25,0.2886751])

    if shape_name == 'rectangle' or shape_name == 'parallelogram':
        if orientation == 'clockwise':
            length_order = [1, 0]
        else:
            length_order = [0, 1, 2]
    if shape_name == 'square':
        catch_point = np.array([0.5,0])

    return catch_point


class Shape:

    def __init__(self, corner_points, color):
        if len(corner_points) <= 2:
            raise NotAShape()
        self.corner_points = corner_points
        self.shape_name = None
        self.color = color
        self.catch_point = None
        self.angle_deviation = None
        self.line_parel_flag1 = False
        self.line_parel_flag2 = False
        self.num_points = len(corner_points)
        self.corner_points = np.array(corner_points)
        self.mass_point = self.corner_points.mean(axis=0)
        self.central_corner_points = self.corner_points - np.tile(self.mass_point, (self.num_points, 1))

        self.vectors = self.central_corner_points - np.insert(
            self.central_corner_points[:-1, :], 0, self.central_corner_points[-1, :], axis=0)
        # 关于如何判定多边形是顺时针还是逆时针对于凸多边形而言，只需对某一个点计算
        # cross product = ((xi - xi-1),(yi - yi-1)) x ((xi+1 - xi),(yi+1 - yi))= (xi - xi-1) * (yi+1 - yi) - (yi - yi-1) * (xi+1 - xi)
        # calculate the cross product then if > 0 it's clockwise,
        # if else then counterclockwise.(Since the coordinate in opencv is different)
        self.orientation = 'clockwise' if np.cross(self.vectors[0], self.vectors[1]) >  0 else 'counterclockwise'
        self.orientation_to_cali = None
        # calculate the line angles
        self.lines_angles = []
        for vector in self.vectors:
            angle = int(math.atan2(vector[1], vector[0])*180/math.pi)
            self.lines_angles.append(angle)
        self.lines_angles = np.asanyarray(self.lines_angles)
        self.intersection_angles = (np.insert(self.lines_angles[:-1], 0, self.lines_angles[-1]) - self.lines_angles) % 360
        self.lengths = np.linalg.norm(self.vectors, axis=1)

    def evaluate_class(self):
        # indicate the status of the Shape class
        if self.corner_points is None:
            return False
        else:
            return True

    def reset(self):
        self.corner_points = None
        self.shape_name = None
        self.angle_deviation = None
        self.line_parel_flag1 = False
        self.line_parel_flag2 = False
        self.num_points = None
        self.corner_points = None
        self.mass_point = None
        self.central_corner_points = None
        self.vectors = None
        self.orientation = None
        self.orientation_to_cali = None
        self.lines_angles = None
        self.intersection_angles = None
        self.lengths = None

    def load_shape(self,corner_points):
        # the same as initialization
        if len(corner_points) <= 2:
            raise NotAShape()
        self.shape_name = None
        self.angle_deviation = None
        self.line_parel_flag1 = False
        self.line_parel_flag2 = False
        self.num_points = len(corner_points)
        self.corner_points = np.array(corner_points)
        self.mass_point = self.corner_points.mean(axis=0)
        self.central_corner_points = self.corner_points - np.tile(self.mass_point, (self.num_points, 1))

        self.vectors = self.central_corner_points - np.insert(
            self.central_corner_points[:-1, :], 0, self.central_corner_points[-1, :], axis=0)
        self.orientation = 'clockwise' if np.cross(self.vectors[0], self.vectors[1]) > 0 else 'counterclockwise'
        self.lines_angles = []
        for vector in self.vectors:
            angle = int(math.atan2(vector[1], vector[0]) * 180 / math.pi)
            self.lines_angles.append(angle)
        self.lines_angles = np.asanyarray(self.lines_angles)
        self.intersection_angles = (np.insert(self.lines_angles[:-1], 0,
                                              self.lines_angles[-1]) - self.lines_angles) % 360
        self.lengths = np.linalg.norm(self.vectors, axis=1)

    def determine_shape(self):

        if self.num_points == 3:
            judgement_equal = self.lengths.std() / self.lengths.mean() < 0.1
            if judgement_equal:
                self.shape_name = 'equilateral triangle'
            else:
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
                if abs(abs(self.lines_angles[0] - self.lines_angles[2]) - 180) < 5:
                    self.line_parel_flag1 = True
                if abs(abs(self.lines_angles[1] - self.lines_angles[3]) - 180) < 5:
                    self.line_parel_flag2 = True
                if self.line_parel_flag1 and self.line_parel_flag2:
                    judgement_diamond = self.lengths.std() / self.lengths.mean() < 0.1
                    if judgement_diamond:
                        self.shape_name = 'diamond'
                    else:
                        self.shape_name = 'parallelogram'
                elif self.line_parel_flag1 or self.line_parel_flag1:
                    self.shape_name = 'ladder'
                else:
                    self.shape_name = 'common quadrilateral'
        # if the shape is a pentagon, it will have 5 vertices
        elif self.num_points == 5:
            self.shape_name = "pentagon"

        # otherwise, we assume the shape is a circle
        else:
            self.shape_name = "circle"

        return self.shape_name

    def determine_rotation(self):
        """
        calculate the according angle the shape need rotating around its mass point in order to turn itself into a calibration
        the angle is in counterclockwise orientation ias default
        :return: angle need to rotate in counterclockwise orientation
        """
        # cali_length_order = get_calibration(self.shape_name,self.orientation)
        # argsort the lengths array to get the index in order from bottom up
        length_order = np.argsort(self.lengths)
        if self.num_points == 3:
            if self.shape_name == 'triangle':
                longest_index = length_order[-1]
                self.angle_deviation = self.lines_angles[longest_index]
            else:
                self.angle_deviation = self.lines_angles[np.argsort(self.lines_angles)[0]]
        elif self.num_points == 4:
            if self.shape_name == 'square' or self.shape_name == 'diamond' :
                self.angle_deviation = self.lines_angles[np.argsort(self.lines_angles)[0]]
            elif self.shape_name == 'rectangle' or self.shape_name == 'parallelogram' or self.shape_name == 'common quadrilateral':
                self.angle_deviation = self.lines_angles[np.argsort(self.lengths)[-1]]
            elif self.shape_name == 'ladder':
                if self.line_parel_flag1:
                    line1 = self.lengths[0]
                    line2 = self.lengths[2]
                    if line1 > line2:
                        index = 0
                    else:
                        index = 2
                elif self.line_parel_flag2:
                    line1 = self.lengths[1]
                    line2 = self.lengths[3]
                    if line1 > line2:
                        index = 1
                    else:
                        index = 3
                self.angle_deviation = self.lines_angles[index]
        elif self.num_points == 5:
            self.angle_deviation = self.lines_angles[np.argsort(self.lines_angles)[0]]

        if self.angle_deviation is not None:
            if self.orientation == 'counterclockwise':
                self.angle_deviation += 180
            if self.angle_deviation > 180:
                self.angle_deviation = 360-self.angle_deviation
                self.orientation_to_cali = 'clockwise'
            else:
                self.orientation_to_cali = 'counterclockwise'
        return self.angle_deviation, self.orientation_to_cali

    def determine_catch_point(self):
        catch_point_cali = get_calibration(self.shape_name,self.orientation)
        if catch_point_cali is None:
            return None
        ratio_to_cali = self.lengths[np.argsort(self.lengths)[-1]]/1
        if self.orientation_to_cali == 'counterclockwise':
            flag = -1
        else:
            flag = 1
        angle_deviation = (flag * self.angle_deviation)/180*np.pi
        cos_theta = np.cos(angle_deviation)
        sin_theta = np.sin(angle_deviation)
        rotation_matrix = np.array([[cos_theta,sin_theta],
                                   [-sin_theta,cos_theta]])
        self.catch_point = self.mass_point + ratio_to_cali*rotation_matrix.dot(catch_point_cali)
        return self.catch_point


