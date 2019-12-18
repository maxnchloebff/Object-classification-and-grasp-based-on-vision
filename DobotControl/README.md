# Introduction

This python module is for the control of a robot arm, which mainly contains part of moving, grabbing, and releasing target (objects with irregular shapes). What's also important is that it needs to communicate with the vision module.

The application target of this python module is the Dobot Magician robot arm manufactured by Dobot company. Based on the DLLs (Dynamic Link Libs) on the official site [Dobot Demo V2.0](https://cn.dobot.cc/downloadcenter/dobot-magician.html?sub_cat=72#sub-download) I've made some enhancement for the convenience of our project:

1. encapsulated the original module into san *myapi.py* file which consists of a class named `DobotMagician`.
2. set the framework for the python main thread (Temporarily I think one thread will be enough, because there is no obvious requirements of small time delay).
3. wrote a calibration file (using *myapi.py*) according to [a CSDN blog](https://blog.csdn.net/heretic1993/article/details/82116742) to compute the transformation matrix between the arm coordinates and the vision coordinates.



# Encapsulation

See *myapi.py* for how to use it.

### Immediate Commands & Queued Commands

Immediate Commands are commands with parameter `is_immediate` set to False, while Queued Commands are the other way round.

**For Queued Commands:** User must first send the commands one by one to the queue, and then use `execute_command_then_stop` method to execute them in order.

**For Immediate Commands:** When they are sent to the Dobot Arm, they will be executed immediately. Use them after method `start_execute_command`; Otherwise they won't work. Note that the method in class `DobotMagician` will automatically let the program in PC to wait for the end of command execution. 

## IO Multiplexing

At last we decided to use electromagnet to grab the blocks, as the pump set can only grab an object at least one surface of which is parallel to the platform.  This, however, contradicts our working conditions.

Totally there are 20 pins available for multiplexing. After exploring, I chose pin 16. The table below shows the properties of pin 16 according to the official user guide:

| I/O address | Voltage | Digital Output | PWM  | Digital Input | ADC  |
| :---------: | :-----: | :------------: | :--: | :-----------: | :--: |
|     16      |   12V   |       √        |  -   |       -       |  -   |

And the methods controlling this pin are now encapsulated to *myapi.py*, which has been roughly tested in the lab (A multimeter showed that the voltage between the 16th pin and GND can switch from 0V to 12V).



**NOTE: Maybe it cannot actuate the electromagnet for its low current.**



# Logic of Program

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



Please try to add "vision module" python scripts inside *main.py* file, because this file is considered to be the "main" and the entry of the whole program.



# (Possible) Future Plans

- [ ] dual thread program. One is named the vision or main module to possess the vision info, and the other communicates with the main thread to control the robots, and at the mean time synchronize with the real Dobot arm.
- [ ] attach the electromagnet to the Dobot arm.



# Log of Recent Progress

## 2019/11/28 and 2019/11/29

- **fatal bug fix:** I didn't add a `dType.SetQueuedCmdStopExec` command after executing the first few commands, which will cause the fact that instantly I send one command to the queue (without start command) the robot will try to execute it and contradicts my expectation. This, may caused chaos inside the robot. After a morning's attempt and with the help of [@maxnchloebff]( https://github.com/maxnchloebff ), I finally realized the problem.
- **some modifications for the convenience of debugging:** As the DLLs doesn't support debugging using python module, I try to add some `print` commands to help me locate where the bug exists.
- Some other utilities.

## 2019/11/30

New function: IO Multiplexing. The related methods are added to the `DobotMagician` class. **Awaiting to be tested in the lab**.

## 2019/12/2

I tested the IO multiplexing code, and it has been proven that this is applicable.

## 2019/12/3 & 2019/12/4

Calibration of arm coordinates and vision coordinates is done. It need to improve precision, though.

Further, as the whole encapsulation is tested generally, I commented all commands with stdout output such as `print`, which are set for the convenience of debugging.

## 2019/12/10

Calibration file improved.

But tests have shown that the electromagnet doesn't work. Maybe the way we use it is incorrect. I will test it further after consort to the Internet. If it doesn't work either, I will try to buy a new one which has higher quality (with a higher price).

