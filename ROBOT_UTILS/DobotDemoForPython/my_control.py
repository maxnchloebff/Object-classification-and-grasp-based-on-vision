from myapi import DobotMagician
import numpy as np
import DobotDllType as dType

"""Global Variables"""


"""Functions directly correlated with the main function"""
# ...


if __name__ == "__main__":
    """
    Initialization of the whole program, including vision and robot
    """
    # vision = Vision()
    # ...

    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()  # self-examine to restore precision

    """
    Working Session, where there are interactions between two modules
    """
    while True:  # "True" can be replaced by a condition: whether or not to continue
        # Robot and Vision module reset:
        # dobot.move(dobot.w_pos, is_immediate=True)  # wait in the waiting position

        """vision: detect the pos of the object"""
        # obj_pos = vision.detect()
        obj_pos = np.array([200, 50, 50, 50])
        """robot: go the the pos"""
        dobot.move(obj_pos)
        dobot.move(obj_pos-[0, 0, 30, 0])
        dobot.end_control(on=True)  # grab the object
        dobot.execute_cmd_on()
        # dType.dSleep(5000)

        """robot: move to the destination platform and release the object"""
        dobot.move(dobot.des_pos)
        dobot.end_control(on=False)
        dobot.execute_cmd_on()

        """vision: check whether there is remaining blocks"""
        # vision.detect_remaining()

