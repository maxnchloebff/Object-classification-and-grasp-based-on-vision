"""
Author: Terence
单位一般均为毫米
"""

import DobotDllType as dType
import numpy as np
import time


CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


class DobotMagician:
    def __init__(self, waiting_pos=np.array([250, 0, 50, 0]), destination_pos=np.array([200, -100, 50, 0])):
        self.api = None
        self.w_pos = waiting_pos
        self.des_pos = destination_pos
        self.last_index = None
        self.move_mode = {"JUMP_XYZ": 0,
                          "MOVJ_XYZ": 1,
                          "MOVL_XYZ": 2,
                          "JUMP_ANGLE": 3,
                          "MOVJ_ANGLE": 4,
                          "MOVL_ANGLE": 5,
                          "MOVJ_ANGLEINC": 6,
                          "MOVL_XYZINC": 7,
                          "MOVJ_XYZINC": 8,
                          "JUMP_MOVLXYZ": 9}

    def disconnect(self):
        dType.DisconnectDobot(self.api)

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
        self.execute_cmd_then_stop()
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
        self.execute_cmd_then_stop()
        self.clear_queue()

    def wait_for_command_execution(self, is_immediate):
        while dType.GetQueuedCmdCurrentIndex(self.api)[0] > self.last_index:
            time.sleep(0.2)

    def move(self, pos, mode=1, is_immediate=False):
        self.last_index = dType.SetPTPCmd(self.api, mode, *pos, isQueued=not is_immediate)[0]
        self.wait_for_command_execution(is_immediate=is_immediate)

    # def move(self, pos, mode=1, is_immediate=False):
    #     if is_immediate:
    #         self.clear_queue()
    #         self.last_index = dType.SetPTPCmd(self.api, mode, *pos, isQueued=0)[0]
    #         while dType.GetQueuedCmdCurrentIndex(self.api)[0] > self.last_index:
    #             print("waiting")
    #             time.sleep(0.2)
    #     else:
    #         self.last_index = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, *pos, isQueued=1)[0]

    def jog(self, is_joint, mode, dest_pos):
        """
        enum {
            IDLE, //空闲状态
            AP_DOWN, //X+/Joint1+
            AN_DOWN, //X-/Joint1-
            BP_DOWN, //Y+/Joint2+
            BN_DOWN, //Y-/Joint2-
            CP_DOWN, //Z+/Joint3+
            CN_DOWN, //Z-/Joint3-
            DP_DOWN, //R+/Joint4+
            DN_DOWN, //R-/Joint4-
            LP_DOWN, //L+。仅在isJoint=1 时，LP_DOWN 可用
            LN_DOWN //L-。仅在isJoint=1 时，LN_DOWN 可用
            };
        :param is_joint: 是否是关节
        :param cmd: 从enum中选一个
        :param is_immediate: 是否立即执行
        """
        self.last_index = dType.SetJOGCmd(self.api, isJoint=is_joint, cmd=mode, isQueued=0)[0]

    def end_control(self, on, is_immediate=False):
        """
        the suction cup control
        :param on: [bool]. True: Suck. False: Loose
        :param is_immediate: [bool]. whether or not to execute instantly the command is sent.
        """
        self.last_index = dType.SetEndEffectorSuctionCup(self.api, enableCtrl=1, on=on, isQueued=not is_immediate)[0]
        self.wait_for_command_execution(is_immediate)

    def get_current_index(self):
        return dType.GetQueuedCmdCurrentIndex(self.api)[0]

    def execute_cmd_then_stop(self, is_clear=True):
        """
        让机械臂执行指令。该指令必须在所有指令均确定了之后再执行。
        """
        dType.SetQueuedCmdStartExec(self.api)
        # Wait for Executing Last Command
        current_index = dType.GetQueuedCmdCurrentIndex(self.api)[0]
        old_current = 0
        while self.last_index > current_index:
            dType.dSleep(100)
            if old_current != current_index:
                print("sleeping" + ", " + "current: ", current_index, "last: ", self.last_index)
                old_current = current_index
            current_index = dType.GetQueuedCmdCurrentIndex(self.api)[0]

        dType.SetQueuedCmdStopExec(self.api)
        if is_clear:
            self.clear_queue()

        print("'execute_cmd_then_stop' returned with index", dType.GetQueuedCmdCurrentIndex(self.api)[0])

    def start_execute_cmd(self):
        dType.SetQueuedCmdStartExec(self.api)

    def end_execute_cmd(self):
        dType.SetQueuedCmdStopExec(self.api)
        
    def wait(self, time, is_immediate=False):
        """
        机械臂等待状态指令，将存续time时间。根据官方API，这个指令只能是队列指令，无法成为立即指令。
        :param time: sleeping time of Dobot (not the pc program) 单位：秒。
        :param is_immediate: 是否立即执行（利用队列清空立即执行）
        """
        self.last_index = dType.SetWAITCmd(self.api, waitTime=time, isQueued=not is_immediate)[0]
        self.wait_for_command_execution(is_immediate)

    def get_pos(self):
        """
        :return: pp: x, y, z, r
                 jp: 4个关节轴的角度
        """
        pose = dType.GetPose(self.api)
        pp = np.array(pose[:4])
        jp = np.array(pose[4:])
        return pp, jp

    def set_mode_digital_output(self, pin=16, is_immediate=False):
        """
        :param pin: 默认的引脚为12
        :param is_immediate:
        :return:
        """
        self.last_index = dType.SetIOMultiplexing(self.api, pin, dType.GPIOType.GPIOTypeDO, isQueued=not is_immediate)[0]
        self.wait_for_command_execution(is_immediate)

    def set_digital_output(self, pin, level, is_immediate=False):
        """
        :param pin:
        :param level: [bool] 高低电平。
        :param is_immediate:
        :return:
        """
        self.last_index = dType.SetIODO(self.api, pin, level, isQueued=not is_immediate)[0]
        self.wait_for_command_execution(is_immediate)


if __name__ == "__main__":
    dobot = DobotMagician()
    dobot.initialize()

    dobot.start_execute_cmd()
    dobot.move(np.array([0, 200, 100, 90]), mode=dobot.move_mode["MOVJ"])
    # dobot.set_home()
    # dobot.start_execute_cmd()
    # temp_pos = dobot.get_pos()[1]
    # dest_pos = np.append(temp_pos[:3], 90)
    # dobot.jog(is_joint=True, mode=7, dest_pos=dest_pos)
    #
    # dobot.start_execute_cmd()
    # dobot.move(dobot.w_pos, is_immediate=True)

    dobot.disconnect()
