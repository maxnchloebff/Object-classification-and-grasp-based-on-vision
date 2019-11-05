# USAGE
# python detect_shapes.py --image shapes_and_colors.png -d False/True

import argparse

# import the necessary packages
from traditional_method.shape_detection.pyimagesearch.shapedetector import Image

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-d", "--debug", required=False, default=True,
	help="whether to set the debug mode(draw some pictures)")
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
image_name = args['image']
debug = args['debug']

if __name__ == '__main__':
    image = Image(debug=True)
    image.read_image(image_name)
    image.detect_shapes()