from myapi import DobotMagician
import numpy as np
import time
# import DobotDllType as dType


if __name__ == "__main__":
    # initialization
    dobot = DobotMagician([250, 0, 50, 0], [200, -100, 50, 0])
    dobot.initialize()
    # dobot.set_home()  # self-examine to restore precision
    print("Finished setting home. Preparing to execute working session commands...")
    print("Position: ", dobot.get_pos()[0], '\n')

    count = 0
    dobot.start_execute_cmd()
    print("Start while loop")
    obj_pos = np.array([200, 100, 50, 0])
    while count < 10:
        dobot.move(obj_pos, mode=1, is_immediate=True)
        print(dobot.last_index)
        time.sleep(5)
        dobot.end_control(on=True, is_immediate=True)  # grab the object
        print(dobot.last_index)
        time.sleep(5)
        # dobot.execute_cmd_then_stop()
        # dType.dSleep(5000)
        # print("Moving to the dest")
        dobot.move(dobot.des_pos, mode=1, is_immediate=True)
        print(dobot.last_index)
        time.sleep(5)
        dobot.end_control(on=False, is_immediate=True)
        print(dobot.last_index)
        time.sleep(5)
        # dobot.execute_cmd_then_stop()
        # print("Position: ", dobot.get_pos()[0], '\n')
        # print(count)

        # vision: check whether there is remaining blocks"""
        # vision.detect_remaining()

        count += 1

    # disconnect dobot:
    dobot.disconnect()
