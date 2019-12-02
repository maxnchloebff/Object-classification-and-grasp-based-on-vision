from myapi import DobotMagician
import time

pin = 16

dobot = DobotMagician()
dobot.initialize()
dobot.set_mode_digital_output(pin=pin, is_immediate=True)
print("Initialized")

dobot.move(dobot.w_pos, is_immediate=True)

for i in range(5):
    dobot.set_digital_output(pin=pin, level=False, is_immediate=True)
    print("Now the output is LOW")
    time.sleep(20)
    dobot.set_digital_output(pin=pin, level=True, is_immediate=True)
    print("Now the output is HIGH")

dobot.disconnect()
