import time
import rsAruco as ra
# import cv2
import numpy as np

from myapi import DobotMagician


if __name__ == "__main__":
    thread1 = ra.cameraDetection(1, "rsArucoDetection")
    if not thread1.isAlive():
        print("camera starts!")
        thread1.start()
    time.sleep(2)

    dobot = DobotMagician(waiting_pos=[250, 0, 50, 0])
    dobot.initialize()
    dobot.set_home()

    default_cali_points = [[180, -60, -5, 0], [270, -60, -5, 0],
                           [180, 60, -5, 0], [270, 60, -5, 0],
                           [270, 80, 35, 0], [180, 80, 35, 0],
                           [180, -80, 35, 0], [270, -80, 35, 0],
                           ]
                           # [200, 150, -5, 0], [250, 150, -5, 0],
                           # [150, 150, 115, 0], [175, 150, 115, 0],
                           # [200, -150, -5, 0], [250, -150, -5, 0],
                           # [150, -150, 115, 0], [175, -150, 115, 0]]

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
    # delete coordinates which resulted from no detection of markers
    cols_to_delete = []
    for i in range(len(centers.transpose())):
        if (centers[0:3, i]==np.array([0, 0, 0])).all():
            centers = np.delete(centers, i, axis=1)
            cols_to_delete.append(i)
    centers = np.delete(centers, cols_to_delete, axis=1)
    arm_cord = np.delete(arm_cord, cols_to_delete, axis=1)


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
    np.save("build/image_to_arm.npy", image_to_arm)
    old_camPt = np.array([-1, -1, -1])
    while True:
        # 让机械臂移动到鼠标点击的点的位置
        if (ra.camPt-np.array([-2, -2, -2])).any() and (ra.camPt-old_camPt).any():
            print("Mouse clicked")
            print("ra.camPt", ra.camPt, "\nold_camPt", old_camPt)
            arm_pos = image_to_arm @ np.append(np.array(ra.camPt), 1)
            arm_pos[3] = 0
            print("arm_pos", arm_pos)
            arm_pos[2] += 100  # 这是用卷尺测量的结果
            # arm_pos[2] += 150
            dobot.start_execute_cmd()
            dobot.move(arm_pos, mode=0, is_immediate=True)  # JUMP_PTP
            time.sleep(1)
            dobot.end_control(on=True, is_immediate=False)
            # dobot.move(np.array([0, 0, -30, 0]), mode=7, is_immediate=True)
            time.sleep(5)
            dobot.move(dobot.des_pos, mode=0, is_immediate=True)
            time.sleep(1)
            dobot.end_control(on=False, is_immediate=False)
            old_camPt = ra.camPt

            alarm_state = dobot.get_alarm_state()
            if alarm_state[2] == 2:  # 当需要机械臂前往的点机械臂认为自己无法到达时，会有这个报警，同时指示灯变红。
                dobot.clear_alarms()
                print("Alarm State Cleared (alarm due to a given pos out of range)")
