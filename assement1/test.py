import brickpi3
import sys
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from motor_driver import MotorDriver

SCALE = eval(" ".join(sys.argv[1:])) if len(sys.argv) > 1 else 2

BP = (
    brickpi3.BrickPi3()
)  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B  # right motor
motorL = BP.PORT_C  # left motor
ROTS_FWD = 4.244 * (38 / 42.5) * 1.12
ROTS = [ROTS_FWD, ROTS_FWD * 40 / 42.5] * 2
ROTS[2] *= 0.97
ROTS_TURN = 1.142 - 0.015
ROTST = [ROTS_TURN] * 4
ROTST[0] *= 0.96
ROTST[1] *= 0.96
ROTST[2] *= 0.97

driver = MotorDriver(motorL, motorR, SCALE)
driver.flipR = True

for ROTS_FWD, ROTS_TURN in zip(ROTS, ROTST):
    driver.move_forward(ROTS_FWD)
    print("Finished fwd")
    driver.rotate(ROTS_TURN)
    print("Finished turn")
