import DobotDllType as dType
import numpy as np


CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


class DobotMagician():
    def __init__(self, waiting_pos=np.array([250, 0, 50, 0]), destination_pos=np.array([0, 200, 50, 0])):
        self.api = None
        self.w_pos = waiting_pos
        self.des_pos = destination_pos
        self.last_index = None

    def initialize(self):
        """
        This function initializes the robot, which includes connection and loading required dll on this computer.
        :return: api (the interface of python)
        """

        # Load Dll
        api = dType.load()

        # Connect Dobot
        state = dType.ConnectDobot(api, "", 115200)[0]
        print("Connect status:", CON_STR[state])

        if state == dType.DobotConnect.DobotConnect_NoError:  # 如果正常连接返回api，如果未正常连接则返回None。
            self.api = api

        # 其他初始化操作和一些参数设置
        dType.SetQueuedCmdClear(self.api)
        dType.SetPTPJointParams(self.api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
        self.last_index = dType.SetPTPCommonParams(self.api, 100, 100, isQueued=1)[0]
        self.execute_cmd_on()
        self.clear_queue()

    def clear_queue(self):
        dType.SetQueuedCmdClear(self.api)

    def set_home(self):
        """
        perform this function at the start of the commands to increase the precision of dobot magician
        :param api: the api
        :return: no return
        """
        # Async Home
        dType.SetHOMEParams(self.api, *self.w_pos, isQueued=1)
        self.last_index = dType.SetHOMECmd(self.api, temp=0, isQueued=1)[0]
        self.execute_cmd_on()
        self.clear_queue()

    def move(self, pos, is_immediate=False):
        if is_immediate:
            self.clear_queue()

        self.last_index = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3],
                                          isQueued=1)[0]

        if is_immediate:
            self.execute_cmd_on()
            self.clear_queue()

    def end_control(self, on, is_immediate=False):
        """
        the suction cup control
        :param on: [bool]. True: Suck. False: Loose
        :param is_immediate: [bool]. whether or not to execute instantly the command is sent.
        """
        if is_immediate:
            self.clear_queue()

        self.last_index = dType.SetEndEffectorSuctionCup(self.api, enableCtrl=1, on=on, isQueued=1)[0]

        if is_immediate:
            self.execute_cmd_on()
            self.clear_queue()

    def execute_cmd_on(self, is_clear=True):
        """
        让机械臂执行指令。该指令必须在所有指令均确定了之后再执行。
        """
        dType.SetQueuedCmdStartExec(self.api)
        # Wait for Executing Last Command
        while self.last_index > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.dSleep(100)

        if is_clear:
            self.clear_queue()

    def execute_cmd_off(self, is_clear=True):
        """
        :param is_clear: whether or not clear the cmd queue. If new commands are on the way and old commands should
        be discarded, is_clear should be set to True.
        """
        # Stop to Execute Command Queued
        dType.SetQueuedCmdStopExec(self.api)
        if is_clear:
            self.clear_queue()


if __name__ == "__main__":
    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()
