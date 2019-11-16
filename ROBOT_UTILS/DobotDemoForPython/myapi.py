import DobotDllType as dType


CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


class DobotMagician():
    def __init__(self):
        self.api = None

    def robot_initialize(self):
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
        dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    def set_home(self, pos):
        """
        perform this function at the start of the commands to increase the precision of dobot magician
        :param api: the api
        :param pos: 1*4[numpy array]
        :return: no return
        """
        # Async Home
        dType.SetHOMECmd(self.api, temp=0, isQueued=1)

        dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3], isQueued=1)

    def move(self, pos):
        dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3], isQueued=1)

    def end_control(self, on):
        """
        the suction cup control
        :param on: [bool]. True: Suck. False: Loose
        """
        dType.SetEndEffectorSuctionCup(self.api, enableCtrl=1, on=on, isQueued=1)