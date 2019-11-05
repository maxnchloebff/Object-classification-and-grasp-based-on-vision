import numpy as np
import math


class Shape():

    def __init__(self,corner_points):
        self.num_points = len(corner_points)
        self.corner_points = np.array(corner_points)
        self.mass_point = self.corner_points.mean(axis=0)
        self.centraled_corner_points = self.corner_points -np.tile(self.mass_point,(self.num_points,1))

        self.vectors = self.centraled_corner_points - np.insert(self.centraled_corner_points[:-1,:],0,self.centraled_corner_points[-1,:],axis=0)
        # calculate the cross product then if > 0 it's clockwise,
        # ifelse then counterclockwise.(Since the coordinate in opencv is different)
        self.orientation = 'clockwise' if np.cross(self.vectors[0], self.vectors[1]) > 0 else 'counter_clockwise'
        # calculate the line angles
        self.lines_angles = []
        for vector in self.vectors:
            angle = int(math.atan2(vector[1],vector[0])*180/math.pi)
            self.lines_angles.append(angle)
        self.lines_angles = np.asanyarray(self.lines_angles)
        self.intersection_angles = (np.insert(self.lines_angles[:-1],0,self.lines_angles[-1]) - self.lines_angles)%360
        self.lengths = np.linalg.norm(self.vectors,axis=1)

    def determin_shape(self):

        if self.num_points == 3:
            self.shape = "triangle"

        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif self.num_points == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio


            judgement_rectangle = self.intersection_angles.std() / self.intersection_angles.mean() < 0.1
            if judgement_rectangle:
                judgement_square = self.lengths.std(axis=0)[0] / self.lengths.mean(axis=0)[0] < 0.1
                if judgement_square:
                    self.shape = 'square'
                else:
                    self.shape = 'rectangle'
            else:
                if abs(abs(self.lines_angles[0] - self.lines_angles[2]) - 180) < 5 and abs(
                        abs(self.lines_angles[1] - self.lines_angles[3]) - 180) < 5:
                    judgement_diamond = self.lengths.std() / self.lengths.mean() < 0.1
                    if judgement_diamond:
                        self.shape = 'diamond'
                    else:
                        self.shape = 'parallelogram'
                elif abs(abs(self.lines_angles[0] - self.lines_angles[2]) - 180) < 5 or abs(
                        abs(self.lines_angles[1] - self.lines_angles[3]) - 180) < 5:
                    self.shape = 'ladder'


        # if the shape is a pentagon, it will have 5 vertices
        elif self.num_points == 5:
            self.shape = "pentagon"

        # otherwise, we assume the shape is a circle
        else:
            self.shape = "circle"

        return self.shape