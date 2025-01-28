
import time
import brickpi3

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
motorR = BP.PORT_B # right motor
motorL = BP.PORT_C # left motor

ROTS_FWD = 4.244
ROTS_TURN = 1.142 - 0.01

for _ in range(4):
    BP.set_motor_position_relative(motorL, 360 * ROTS_FWD)
    BP.set_motor_position_relative(motorR, 360 * ROTS_FWD)

    time.sleep(0.5)
    print("Finished fwd")

    BP.set_motor_position_relative(motorL, 360 * ROTS_TURN)
    BP.set_motor_position_relative(motorR, -360 * ROTS_TURN)

    time.sleep(0.5)
    print("Finished rotating")
