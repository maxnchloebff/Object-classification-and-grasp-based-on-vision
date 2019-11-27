import DobotDllType as dType


CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


class DobotMagician():
    def __init__(self):
        self.api = None
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
        dType.SetQueuedCmdClear(api)
        dType.SetHOMEParams(self.api, 250, 0, 50, 0, isQueued=1)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
        self.last_index = dType.SetPTPCommonParams(api, 100, 100, isQueued=1)[0]

    def set_home(self):
        """
        perform this function at the start of the commands to increase the precision of dobot magician
        :param api: the api
        :param pos: 1*4[numpy array]
        :return: no return
        """
        # Async Home
        self.last_index = dType.SetHOMECmd(self.api, temp=0, isQueued=1)[0]

    def move(self, pos):
        self.last_index = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3],
                                          isQueued=1)[0]

    def end_control(self, on):
        """
        the suction cup control
        :param on: [bool]. True: Suck. False: Loose
        """
        self.last_index = dType.SetEndEffectorSuctionCup(self.api, enableCtrl=1, on=on, isQueued=1)[0]

    def execute_cmd(self):
        """
        让机械臂执行指令。该指令必须在所有指令均确定了之后再执行。
        """
        dType.SetQueuedCmdStartExec(self.api)
        # Wait for Executing Last Command
        while self.last_index > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.dSleep(100)

        # Stop to Execute Command Queued
        dType.SetQueuedCmdStopExec(self.api)


if __name__ == "__main__":
    dobot = DobotMagician()
    dobot.initialize()
    dobot.set_home()
    dobot.execute_cmd()
