import time
import rsAruco as ra
import cv2
import numpy as np

from myapi import DobotMagician


if __name__ == "__main__":
    thread1 = ra.cameraDetection(1, "rsArucoDetection")
    if not thread1.isAlive():
        print("camera starts!")
        thread1.start()
    time.sleep(2)

    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()

    default_cali_points = [[180, -120, 135, 0], [270, -120, 135, 0],
                           [180, 120, 135, 0], [270, 120, 135, 0],
                           [270, 120, -5, 0], [180, 120, -5, 0],
                           [180, -120, -5, 0], [270, -120, -5, 0],
                           [200, 150, -5, 0], [250, 150, -5, 0],
                           [150, 150, 115, 0], [175, 150, 115, 0],
                           [200, -150, -5, 0], [250, -150, -5, 0],
                           [150, -150, 115, 0], [175, -150, 115, 0]]

    np_cali_points = np.array(default_cali_points)
    arm_cord = np.column_stack((np_cali_points[:, 0:3], np.ones(np_cali_points.shape[0]).T)).T

    dobot.start_execute_cmd()

    centers = np.ones(arm_cord.shape)

    for ind, pt in enumerate(default_cali_points):
        print("Current points:", pt)
        dobot.move(pt, is_immediate=True)
        time.sleep(2)
        centers[0:3, ind] = ra.center * 1000
        print(ra.center)

    image_to_arm = np.dot(arm_cord, np.linalg.pinv(centers))
    arm_to_image = np.linalg.pinv(image_to_arm)
    dobot.move(np.array([217, 0, 154, 0]), is_immediate=True)
    dobot.end_execute_cmd()

    print("Finished")
    print("Image to arm transform:\n", image_to_arm)
    print("Arm to Image transform:\n", arm_to_image)

    print("Sanity Test:")

    print("-------------------")
    print("Image_to_Arm")
    print("-------------------")
    for ind, pt in enumerate(centers.T):
        print("Expected:", default_cali_points[ind][0:3])
        print("Result:", np.dot(image_to_arm, np.array(pt))[0:3])

    print("-------------------")
    print("Arm_to_Image")
    print("-------------------")
    for ind, pt in enumerate(default_cali_points):
        print("Expected:", centers.T[ind][0:3])
        pt[3] = 1
        print("Result:", np.dot(arm_to_image, np.array(pt))[0:3])

    print("-------------------")
    print("示教运动")
    print("-------------------")
    old_camPt = np.array([-1, -1, -1])
    while True:
        # 让机械臂移动到鼠标点击的点的位置
        if (ra.camPt-np.array([-2, -2, -2])).any and (ra.camPt-old_camPt).any():
            arm_pos = image_to_arm @ np.array(ra.camPt)
            dobot.start_execute_cmd()
            dobot.move(arm_pos, is_immediate=True)
            old_camPt = ra.camPt
