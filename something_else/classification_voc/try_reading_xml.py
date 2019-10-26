import xml.etree.cElementTree as et
import os
import re
root = '/media/kai/DATA/dataset/VOC/VOCdevkit/VOC2012'
xml_root = os.path.join(root,"Annotations")
original_image_root = os.path.join(root,"JPEGImages")

xml_files = os.listdir(xml_root)
inputfile = open('/home/kai/person_jpgs.txt','w')
is_person = 0
for file in xml_files:
    if not file.endswith('.xml'):
        continue
    full_file_path = os.path.join(xml_root,file)
    xml_tree = et.ElementTree(file=full_file_path)
    root = xml_tree.getroot()

    for sub_node in root:
        # print("The sub_node tag is " + sub_node.tag)
        if is_person == 1:
            print("This is a person image.")
            inputfile.write(filename+'\n')
            is_person = 0
            break
        if sub_node.tag == 'filename':
            filename = sub_node.text
            print(filename)
        if sub_node.tag == 'object':
            for node in sub_node:
                if node.tag == 'name':
                    if node.text == 'person':
                        is_person = 1
                        break
                # print("     The node tag is " + node.tag)
inputfile.close()