# 1. Module Introduction

This python module is for the control of a robot arm, which mainly contains part of moving, grabbing, and releasing target (objects with irregular shapes). What's also important is that it needs to communicate with the vision module.

The application target of this python module is the Dobot Magician robot arm manufactured by Dobot company. Based on the DLLs (Dynamic Link Libs) on the official site [Dobot Demo V2.0](https://cn.dobot.cc/downloadcenter/dobot-magician.html?sub_cat=72#sub-download) I've made some enhancement for the convenience of our project:

1. encapsulated the original module into an *myapi.py* file which consists of a class named `DobotMagician`.
2. set the framework for the python main thread (**Temporarily I think one thread will be enough, because there is no obvious requirements of small time delay**).



# 2. Usage

See *myapi.py* for how to use it.

## 2.1 Logic of Program

See the semi-pseudo python code below for the logic of the program.

```python
from myapi import DobotMagician
import numpy as np

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
        dobot.move(dobot.w_pos, is_immediate=True)  # wait in the waiting position

        """vision: detect the pos of the object"""
        # obj_pos = vision.detect()
        """robot: go the the pos"""
        dobot.move(obj_pos)
        dobot.end_control(on=True)  # grab the object
        dobot.execute_cmd_on()

        """robot: move to the destination platform and release the object"""
        dobot.move(dobot.des_pos)
        dobot.end_control(on=False)
        dobot.execute_cmd_on()

        """vision: check whether there is remaining blocks"""
        # vision.detect_remaining()
```



Please try to add "vision module" python scripts inside *my_control.py* file, because this file is considered to be the "main" and the entry of the whole program.

**Note:** methods in `DobotMagician`, such as `initialize`, `set_home` and `move` involve commands which are firstly stored inside a queue. Only after method `execute_cmd` is executed, the commands in queue will be executed by the arm in order.



# Problems

There exist problems when it comes to my understanding of the Dobot Magician robot arm:

- [ ] What is the python grammar pattern when I need to set `isQueued = 0`? In other words, how do the robot arm respond when it receives a command which is not in the queue? I've made a test in the lab, but the command wasn't executed. **(My temporary resolution, however, exists - the queue will be cleared, added by one command, and executed consecutively. This, I think, may reduce the efficiency*)**