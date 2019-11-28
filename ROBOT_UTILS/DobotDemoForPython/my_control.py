from myapi import DobotMagician
import numpy as np
# import DobotDllType as dType


if __name__ == "__main__":
    # initialization
    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()  # self-examine to restore precision
    print("Finished setting home. Preparing to execute working session commands...")

    while True:  # "True" can be replaced by a condition: whether or not to continue
        # Robot and Vision module reset:
        dobot.move(dobot.w_pos, is_immediate=True)  # wait in the waiting position

        # obj_pos = vision.detect()
        obj_pos = np.array([200, 50, 50, 50])

        dobot.move(obj_pos)
        # dobot.move(obj_pos-[0, 0, 30, 0])
        dobot.end_control(on=True)  # grab the object
        dobot.execute_cmd_then_stop()
        # dType.dSleep(5000)

        dobot.move(dobot.des_pos)
        dobot.wait(1000)
        dobot.end_control(on=False)
        dobot.execute_cmd_then_stop()

        """vision: check whether there is remaining blocks"""
        # vision.detect_remaining()

