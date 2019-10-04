import xml.etree.cElementTree as et
import pandas as pd
import cv2
import os
import re
root = '/media/kai/DATA/dataset/VOC/VOCdevkit/VOC2012'
xml_root = os.path.join(root,"Annotations")
original_image_root = os.path.join(root,"JPEGImages")
def append_lines_to_current_image(image,bnd_ls):
    xmin = bnd_ls[0]
    ymin = bnd_ls[1]
    xmax = bnd_ls[2]
    ymax = bnd_ls[3]
    cv2.line(image, (xmin, ymin), (xmin, ymax), (255, 0, 0), 5)
    cv2.line(image, (xmin, ymax), (xmax, ymax), (255, 0, 0), 5)
    cv2.line(image, (xmax, ymax), (xmax, ymin), (255, 0, 0), 5)
    cv2.line(image, (xmax, ymin), (xmin, ymin), (255, 0, 0), 5)
if __name__ == '__main__':
    person_image_llifes = open('/home/kai/person_jpgs.txt','r')
    while True:
        line = person_image_llifes.readline().split('.jpg\n')
        if len(line) == 1:
            break
        current_xml_name = line[0]+'.xml'
        current_jpg_name = line[0]+'.jpg'
        current_image = cv2.imread(os.path.join(original_image_root,current_jpg_name))
        xml_tree = et.ElementTree(file=os.path.join(xml_root,current_xml_name))
        root  = xml_tree.getroot()
        for sub_node in root:
            if sub_node.tag == 'object' :
                is_person = 0
                for node in sub_node:
                    if node.tag == 'name' and node.text == 'person':
                        is_person = 1
                    if is_person == 0:
                        break
                    if node.tag == 'bndbox':
                        bnd_list = []
                        for bnd in node:
                            bnd_list.append(int(bnd.text))
                        append_lines_to_current_image(current_image,bnd_list)
                        break


        cv2.imshow('current_image',current_image)
        cv2.waitKey(0)