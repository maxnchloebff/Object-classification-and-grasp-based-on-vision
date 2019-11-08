import threading
import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

# Load Dll
api = dType.load()

# Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("Connect status:",CON_STR[state])

if state == dType.DobotConnect.DobotConnect_NoError:

    # Clean Command Queued
    dType.SetQueuedCmdClear(api)

    # Async Motion Params Setting
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued = 1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # Async Home
    dType.SetHOMECmd(api, temp=0, isQueued=1)

    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 200, 0, 50, 0, isQueued=1)  # 前往不干扰全局摄像头的初始点

    ######################
    target = [0, 0, 0, 0]
    # .......
    # 这里是视觉系统识别的方法，最终返回target作为机械臂抓取的物块点
    ######################

    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, target[0], target[1], target[2], target[3], isQueued=1)

    dType.SetEndEffectorSuctionCup(api, enableCtrl=1, on=1, isQueued=1)  # 气泵吸气，抓取物块

    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 200, 200, 50, 0, isQueued=1)  # 前往目标平台

    dType.SetEndEffectorSuctionCup(api, enableCtrl=1, on=0, isQueued=1)  # 气泵吹气， 放下物块
    lastIndex = dType.SetEndEffectorSuctionCup(api, enableCtrl=0, on=1, isQueued=1)  # 关闭气泵

    # Start to Execute Command Queued
    dType.SetQueuedCmdStartExec(api)

    # Wait for Executing Last Command
    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)

    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)

# Disconnect Dobot
dType.DisconnectDobot(api)
