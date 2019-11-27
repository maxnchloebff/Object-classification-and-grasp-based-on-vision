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
print("Connect status:",CON_STR[state])

if state == dType.DobotConnect.DobotConnect_NoError:

    # Clean Command Queued
    dType.SetQueuedCmdClear(api)

    # Async Motion Params Setting
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued=0)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=0)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=0)

    # Async Home
    dType.SetHOMECmd(api, temp=0, isQueued=0)
    dType.dSleep(1000)

# Disconnect Dobot
dType.DisconnectDobot(api)
