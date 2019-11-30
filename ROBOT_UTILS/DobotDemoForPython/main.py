from myapi import DobotMagician
import numpy as np
# import DobotDllType as dType


if __name__ == "__main__":
    # initialization
    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()  # self-examine to restore precision
    print("Finished setting home. Preparing to execute working session commands...")
    print("Position: ", dobot.get_pos()[0], '\n')

    count = 0
    while count < 10:
        # Robot and Vision module reset:
        dobot.move(dobot.w_pos, is_immediate=True)  # wait in the waiting position
        print("Position: ", dobot.get_pos()[0])

        # obj_pos = vision.detect()
        obj_pos = np.array([200, 100, 50, 50])

        dobot.move(obj_pos)
        # dobot.move(obj_pos-[0, 0, 30, 0])
        # dobot.end_control(on=True)  # grab the object
        dobot.execute_cmd_then_stop()
        # dType.dSleep(5000)

        dobot.move(dobot.des_pos)
        dobot.wait(1)
        # dobot.end_control(on=False)
        dobot.execute_cmd_then_stop()
        print("Position: ", dobot.get_pos()[0], '\n')

        # vision: check whether there is remaining blocks"""
        # vision.detect_remaining()

        count += 1

    # disconnect dobot:
    dobot.disconnect()