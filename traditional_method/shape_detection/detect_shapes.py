# USAGE
# python detect_shapes.py --image shapes_and_colors.png -d False/True

import argparse

# import the necessary packages
from traditional_method.shape_detection.pyimagesearch.ImageType import Image

# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
#                 help="path to the input image")
# ap.add_argument("-d", "--debug", required=False, default=True,
#                 help="whether to set the debug mode(draw some pictures)")
# args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
# image_name = args['image']
# debug = args['debug']
image_name = 'adjoin.png'
if __name__ == '__main__':
    image = Image(debug=True)
    image.only_read(image_name)
    image.detect_by_color(color='red', draw=True)
    image.detect_by_color(color='green', draw=True)
    image.detect_by_color(color='blue', draw=True)
    print('当前图片中一共有'+str(len(image.Shapes))+'个形状')
    print('它们分别是')
    i = 1
    for shape in image.Shapes:
        print('#################################')
        print(str(i), '. ', shape.color, shape.shape_name)
        i += 1
    # image.detect_shapes()
