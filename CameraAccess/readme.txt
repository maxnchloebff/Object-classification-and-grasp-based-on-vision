JHCap2.dll是驱动相机所需函数的动态链接库，需要拷贝到文件夹目录下才能运行loop.py，读取摄像头图像。

loop.py为官方例程

loop_feature_extraction.py是一个例子，读取图像，识别特征点并计算描述子

package dependency : ctypes, numpy, cv2