import numpy as np
from myapi import DobotMagician
import rsAruco as ra
import time

thread1 = ra.cameraDetection(1, "rsArucoDetection")
if not thread1.is_alive():
    print("camera starts!")
    thread1.start()

time.sleep(2)

dobot = DobotMagician(waiting_pos=[250, 0, 50, 0], destination_pos=[200, -100, 50, 0])
dobot.initialize()
dobot.set_home()

dobot.start_execute_cmd()
old_camPt = np.array([-1, -1, -1])
image_to_arm = np.load('build/image_to_arm.npy')
while True:
    # 让机械臂移动到鼠标点击的点的位置
    if (ra.camPt - np.array([-2, -2, -2])).any() and (ra.camPt - old_camPt).any():
        print("Mouse clicked")
        print("ra.camPt", ra.camPt, "\nold_camPt", old_camPt)
        arm_pos = image_to_arm @ np.append(np.array(ra.camPt), 1)
        arm_pos[3] = 0
        print("arm_pos", arm_pos)
        arm_pos[2] += 115  # 这是用卷尺测量的结果
        # arm_pos[2] += 150
        dobot.start_execute_cmd()
        dobot.move(arm_pos, mode=0, is_immediate=True)  # JUMP_PTP
        time.sleep(1)
        dobot.end_control(on=True, is_immediate=False)
        # dobot.move(np.array([0, 0, -30, 0]), mode=7, is_immediate=True)
        time.sleep(5)
        dobot.move(dobot.des_pos, mode=0, is_immediate=True)
        dobot.move([0, 0, -100, 0], mode=7, is_immediate=True)
        time.sleep(1)
        dobot.end_control(on=False, is_immediate=False)
        dobot.move([0, 0, 100, 0], mode=7, is_immediate=True)

        old_camPt = ra.camPt

        alarm_state = dobot.get_alarm_state()
        if alarm_state[2] == 2:  # 当需要机械臂前往的点机械臂认为自己无法到达时，会有这个报警，同时指示灯变红。
            dobot.clear_alarms()
            print("Alarm State Cleared (alarm due to a given pos out of range)")