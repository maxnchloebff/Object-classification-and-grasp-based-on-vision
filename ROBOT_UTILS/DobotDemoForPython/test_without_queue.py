"""
TEST HASN'T PASSED YET
"""

import DobotDllType as dType


CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

# Load Dll
api = dType.load()

# Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("Connect status:", CON_STR[state])

if state == dType.DobotConnect.DobotConnect_NoError:

    # Clean Command Queued
    dType.SetQueuedCmdClear(api)

    # Async Motion Params Setting
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)
    lastIndex = dType.SetHOMECmd(api, temp=0, isQueued=1)[0]
    dType.SetQueuedCmdStartExec(api)

    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
        print("sleeping" + ", " + "current: ", dType.GetQueuedCmdCurrentIndex(api)[0],
              "last: ", lastIndex)

    # 立即指令
    print("Now trying to execute immediate commands...")
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 200, 50, 50, 50, isQueued=0)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVJXYZMode, 0, -200, 100, 0, isQueued=0)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVJXYZMode, 0, 200, 50, 0, isQueued=0)

    dType.dSleep(10000)
    print("immediate commands ended")

    dType.SetQueuedCmdStopExec(api)

# Disconnect Dobot
dType.DisconnectDobot(api)
print("Dobot disconnected")
