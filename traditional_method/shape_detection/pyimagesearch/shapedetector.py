# import the necessary packages
import cv2
import math
import operator
def cal_angle(v1,v2):
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


def get_calibration(shape_name):
	if shape_name == 'triangle':
		length_order=[0,2,1]
		return length_order



class ShapeDetector:
	def __init__(self):
		pass

	def detect(self, c):
		# initialize the shape name and approximate the contour
		shape = "unidentified"
		angle = 0
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)
		corner_points = [[point[0][0],point[0][1]] for point in approx]
		mass_point = [0,0]
		for point in corner_points:
			mass_point[0] += point[0]
			mass_point[1] += point[1]
		mass_point[0] /= len(corner_points)
		mass_point[1] /= len(corner_points)
		cenral_corner_points =[[point[0]-mass_point[0],point[1]-mass_point[1]] for point in corner_points]
		vectors = [[(corner_points[i][0]-corner_points[i-1][0]),(corner_points[i][1]-corner_points[i-1][1])] for i in range(len(corner_points))]
		angles = []
		for i in range(len(vectors)):
			angles.append(int(math.atan2(vectors[i][1],vectors[i][0])*180/math.pi))

		angles_between = []
		for i in range(len(vectors)-1):
			angles_between.append(cal_angle(vectors[i],vectors[i+1]))
		angles_between.append(cal_angle(vectors[-1], vectors[0]))
		# order the the corner points according to the length of each vector
		lengths = []
		for i in range(len(vectors)):
			lengths.append([pow(vectors[i][0],2)+pow(vectors[i][1],2),i])
		lengths.sort(key=lambda x:x[0])
		length_order = [pair[1] for pair in lengths]
		# if the shape is a triangle, it will have 3 vertices
		if len(approx) == 3:
			shape = "triangle"
			cali_order = get_calibration(shape)
			first_cali_element = cali_order[0]
			first_actual_element = length_order[0]
			move = abs(first_actual_element-first_cali_element)%3
			angle =math.atan2(vectors[move][1], vectors[move][0])
			angle = int(angle * 180 / math.pi)



		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		elif len(approx) == 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)

			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
			if shape == 'square':
				absAngles = map(abs, angles)
				absAngles = list(absAngles)
				angle = angles[absAngles.index(min(absAngles))]
			else:
				absAngles = map(abs, angles)
				absAngles = list(absAngles)
				angle = angles[absAngles.index(min(absAngles))]

		# if the shape is a pentagon, it will have 5 vertices
		elif len(approx) == 5:
			shape = "pentagon"
			absAngles = map(abs,angles)
			absAngles = list(absAngles)
			angle = angles[absAngles.index(min(absAngles))]

		# otherwise, we assume the shape is a circle
		else:
			shape = "circle"
			angle = None

		# return the name of the shape
		return shape, approx, angle